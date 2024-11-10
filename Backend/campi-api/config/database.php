<?php
class Database {
    private $host = "localhost";
    private $db_name = "campi_db";
    private $username = "root";
    private $password = "";  // Default XAMPP MySQL password is blank
    public $conn;

    public function getConnection() {
        $this->conn = null;

        try {
            $this->conn = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->db_name,
                $this->username,
                $this->password
            );
            // Set error mode to exception for better error handling
            $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            
            // Set character set to UTF-8
            $this->conn->exec("set names utf8");
            
        } catch(PDOException $e) {
            echo "Connection Error: " . $e->getMessage();
        }

        return $this->conn;
    }
}
?>