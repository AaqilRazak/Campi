<?php
// Add these headers at the very top of the file
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");
header("Content-Type: application/json; charset=UTF-8");

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

include_once '../config/database.php';

// For debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

$database = new Database();
$db = $database->getConnection();

// Get posted data
$data = json_decode(file_get_contents("php://input"));

if (!empty($data->username) && !empty($data->password)) {
    $query = "SELECT ui.UserID, ui.Username, ui.PasswordHash, ui.Email, 
              ui.FirstName, ui.LastName, ur.RoleName 
              FROM UserInformation ui 
              JOIN UserRoles ur ON ui.UserRoleID = ur.UserRoleID 
              WHERE ui.Username = ?";
    
    $stmt = $db->prepare($query);
    $stmt->execute([$data->username]);
    
    if ($stmt->rowCount() > 0) {
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if (password_verify($data->password, $row['PasswordHash'])) {
            // Create session log
            $sessionQuery = "INSERT INTO SessionLogs 
                           (UserID, SessionStartTime, DeviceType, IPAddress, BrowserAgent) 
                           VALUES (?, NOW(), ?, ?, ?)";
            
            $stmt = $db->prepare($sessionQuery);
            $deviceType = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown';
            $ipAddress = $_SERVER['REMOTE_ADDR'] ?? 'Unknown';
            $browserAgent = $_SERVER['HTTP_USER_AGENT'] ?? 'Unknown';
            
            $stmt->execute([
                $row['UserID'],
                $deviceType,
                $ipAddress,
                $browserAgent
            ]);
            
            $sessionId = $db->lastInsertId();
            
            // Generate token
            $token = bin2hex(random_bytes(32));
            
            http_response_code(200);
            echo json_encode([
                "success" => true,
                "token" => $token,
                "sessionId" => $sessionId,
                "user" => [
                    "id" => $row['UserID'],
                    "username" => $row['Username'],
                    "email" => $row['Email'],
                    "firstName" => $row['FirstName'],
                    "lastName" => $row['LastName'],
                    "role" => $row['RoleName']
                ]
            ]);
        } else {
            http_response_code(401);
            echo json_encode([
                "success" => false,
                "message" => "Invalid credentials"
            ]);
        }
    } else {
        http_response_code(401);
        echo json_encode([
            "success" => false,
            "message" => "User not found"
        ]);
    }
} else {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "message" => "Username and password are required"
    ]);
}
?>