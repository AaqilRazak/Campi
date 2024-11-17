<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header("Access-Control-Allow-Credentials: true");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Direct connection to teammate's database
$db = new PDO(
    "mysql:host=69.215.107.194;dbname=campiDB",
    "teammate_username",    // Replace with actual username
    "teammate_password",    // Replace with actual password
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

// Get request data
$data = json_decode(file_get_contents("php://input"));
$action = $_GET['action'] ?? '';

switch($action) {
    case 'login':
        if (empty($data->username) || empty($data->password)) {
            echo json_encode(["success" => false, "message" => "Missing credentials"]);
            exit();
        }

        $stmt = $db->prepare("
            SELECT ui.UserID, ui.Username, ui.PasswordHash, ui.FirstName, 
                   ui.LastName, ur.RoleName 
            FROM UserInformation ui 
            JOIN UserRoles ur ON ui.UserRoleID = ur.UserRoleID 
            WHERE ui.Username = ?
        ");
        
        $stmt->execute([$data->username]);
        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user && password_verify($data->password, $user['PasswordHash'])) {
            // Create session
            $stmt = $db->prepare("
                INSERT INTO SessionLogs (UserID, SessionStartTime) 
                VALUES (?, NOW())
            ");
            $stmt->execute([$user['UserID']]);
            $sessionId = $db->lastInsertId();

            echo json_encode([
                "success" => true,
                "sessionId" => $sessionId,
                "user" => [
                    "id" => $user['UserID'],
                    "username" => $user['Username'],
                    "firstName" => $user['FirstName'],
                    "lastName" => $user['LastName'],
                    "role" => $user['RoleName']
                ]
            ]);
        } else {
            echo json_encode(["success" => false, "message" => "Invalid credentials"]);
        }
        break;

    case 'logout':
        if (empty($data->sessionId)) {
            echo json_encode(["success" => false, "message" => "No session ID"]);
            exit();
        }

        $stmt = $db->prepare("
            UPDATE SessionLogs 
            SET SessionEndTime = NOW() 
            WHERE SessionID = ?
        ");
        
        $stmt->execute([$data->sessionId]);
        echo json_encode(["success" => true]);
        break;

    default:
        echo json_encode(["success" => false, "message" => "Invalid action"]);
}
?> 