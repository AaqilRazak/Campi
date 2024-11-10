<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");

include_once '../config/database.php';

$database = new Database();
$db = $database->getConnection();

$data = json_decode(file_get_contents("php://input"));

if (!empty($data->sessionId)) {
    $query = "UPDATE SessionLogs SET SessionEndTime = NOW() 
              WHERE SessionID = ? AND SessionEndTime IS NULL";
    
    $stmt = $db->prepare($query);
    
    if ($stmt->execute([$data->sessionId])) {
        http_response_code(200);
        echo json_encode([
            "success" => true,
            "message" => "Logged out successfully"
        ]);
    } else {
        http_response_code(500);
        echo json_encode([
            "success" => false,
            "message" => "Error updating session"
        ]);
    }
} else {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "message" => "Session ID is required"
    ]);
}
?> 