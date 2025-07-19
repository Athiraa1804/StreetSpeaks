<?php
$servername = "localhost";
$username = "root";
$password = ""; // Leave blank if no password
$dbname = "streetspeaks";
$port = 3307; // Important: You changed MySQL port!

$conn = new mysqli($servername, $username, $password, $dbname, $port);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
