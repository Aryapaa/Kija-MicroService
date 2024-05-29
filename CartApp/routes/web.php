<?php

/** @var \Laravel\Lumen\Routing\Router $router */

/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
|
| Here is where you can register all of the routes for an application.
| It is a breeze. Simply tell Lumen the URIs it should respond to
| and give it the Closure to call when that URI is requested.
|
*/

$router->get('/cart', 'CartController@getCart');
$router->get('/cart/{idUser}', 'CartController@getCartByUser');
$router->post('/add_to_cart', 'CartController@addToCart');
$router->post('/cart/delete', 'CartController@deleteFromCart');

$router->get('/', function () use ($router) {
    return $router->app->version();
});
