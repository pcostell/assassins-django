<?php

/******************************************
 * Simple PHP Stanford WebAuth script
 * ---
 * Allows an external server to have trusted Stanford WebAuth authentication without setting up mod_webauth, which
 * is annoying to setup.
 *
 * Be sure to change the $SHARED_SECRET!
 *
 * Maintained by: Stephen Trusheim (tru@sse.stanford)
 * Original Author: Quinn Slack (sqs@cs.stanford)
 */


$SHARED_SECRET = 'FILL_ME';

// ---------------------------------------------


function generateNonce($length) {
        $charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        $key = '';
        for ($i=0; $i<$length; $i++) {
            $key .= $charset[(mt_rand(0,(strlen($charset)-1)))];
        }
        return $key;
}

$protocol = "WA_2";

$sunetId = $_SERVER['WEBAUTH_USER'];
$sunetId_64 = base64_encode($sunetId);
$displayName_64 = base64_encode($_SERVER['WEBAUTH_LDAP_DISPLAYNAME']);

$nonce = generateNonce(16);

$hash = sha1($SHARED_SECRET . $nonce . $sunetId);
$hashStr = $nonce . '$' . $hash;

$return = $_GET['return'];

$next = $_GET['next'];
$next_64 = base64_encode($next);

header("Location: $return?WA_prot=$protocol&WA_user=$sunetId_64&WA_hash=$hashStr&WA_name=$displayName_64&WA_next=$next_64");