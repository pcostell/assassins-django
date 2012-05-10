<?php

$SHARED_SECRET = 'test';

function generateNonce($length) {
        $charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        $key = '';
        for ($i=0; $i<$length; $i++) {
            $key .= $charset[(mt_rand(0,(strlen($charset)-1)))];
        }
        return $key;
}

$protocol = "WA_2";

$sunetId = $_GET['login_as'];
if ($sunetId == '') {
    $sunetId = $_SERVER['WEBAUTH_USER'];
}

$sunetId_64 = base64_encode($sunetId);
$displayName = $_GET['display_name'];
if ($displayName == '') {
    $displayName = $_SERVER['WEBAUTH_LDAP_DISPLAYNAME'];
}
$displayName_64 = base64_encode($displayName);

$nonce = generateNonce(16);

$hash = sha1($SHARED_SECRET . $nonce . $sunetId);
$hashStr = $nonce . '$' . $hash;

$return = $_GET['return'];

$next = $_GET['next'];
$next_64 = base64_encode($next);

$submitted = isset($_GET['continue']);
if (!$submitted) {
    print "<form method = 'GET' action = ''>Return: <input type = 'text' name = 'return' value = '$return' size = 100><br />Next: <input type = 'text' name = 'next' value = '$next' size = 100><br />Login: <input type = 'text' name = 'login_as' value = '$sunetId' /><br />DName: <input type = 'text' name = 'display_name' value = '$displayName' /><br /><input type = 'submit' name = 'continue' value = 'Login'></form>";
    exit;
}

header("Location: $return?WA_prot=$protocol&WA_user=$sunetId_64&WA_hash=$hashStr&WA_name=$displayName_64&WA_next=$next_64");