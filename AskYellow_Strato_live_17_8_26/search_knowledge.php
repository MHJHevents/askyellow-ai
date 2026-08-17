<?php
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Origin: *");

$q = isset($_POST['q']) ? strtolower(trim($_POST['q'])) : "";

if ($q === "") {
    echo json_encode(["shop" => []]);
    exit;
}

/* -------------------------------------------------------------
   1) LOAD SHOP DATA (STATIC JSON OR SHOPIFY API)
--------------------------------------------------------------*/

// SNELSTE EN EERSTE VERSIE → laad jouw product JSON lokaal
// Later kunnen we Shopify API integreren

$products = json_decode(file_get_contents("products.json"), true);

/* -------------------------------------------------------------
   2) SEARCH
--------------------------------------------------------------*/

$matches = [];

foreach ($products as $p) {
    $haystack = strtolower($p["title"] . " " . $p["tags"] . " " . $p["description"]);

    if (strpos($haystack, $q) !== false) {
        $matches[] = [
            "title" => $p["title"],
            "url"   => $p["url"],
            "image" => $p["image"]
        ];
    }
}

/* -------------------------------------------------------------
   3) RESPONSE
--------------------------------------------------------------*/

echo json_encode([
    "shop" => $matches
]);
exit;
?>

