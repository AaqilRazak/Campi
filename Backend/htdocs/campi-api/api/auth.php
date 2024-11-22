<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

try {
    $rawData = file_get_contents("php://input");
    $data = json_decode($rawData);
    
    $db = new PDO(
        "mysql:host=localhost;dbname=campi_db",
        "root",
        "",
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
    
    $stmt = $db->prepare("
        SELECT ui.*, ur.RoleName 
        FROM UserInformation ui 
        JOIN UserRoles ur ON ui.UserRoleID = ur.UserRoleID 
        WHERE ui.Username = ? AND ui.PasswordHash = ?
    ");
    
    $stmt->execute([$data->username, $data->password]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($user) {
        echo json_encode([
            "success" => true,
            "user" => [
                "id" => $user['UserID'],
                "username" => $user['Username'],
                "role" => $user['RoleName'],
                "firstName" => $user['FirstName'],
                "lastName" => $user['LastName']
            ]
        ]);
    } else {
        echo json_encode([
            "success" => false,
            "message" => "Invalid credentials"
        ]);
    }
    
} catch (Exception $e) {
    echo json_encode([
        "success" => false,
        "message" => "Server error: " . $e->getMessage()
    ]);
}
?>