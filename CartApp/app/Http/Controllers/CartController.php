<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Response;
use GuzzleHttp\Client;

class CartController extends Controller
{
    private $hasura_url = 'https://flying-dingo-28.hasura.app/v1/graphql';
    private $hasura_secret = 'VMk2qKcMIReoIA5H82r0JX6XE2OGJ442lPPdyjDfHmnx6Dg3VTs8T52kxENOOKUV';

    private function fetchCartsFromHasura($idUser)
    {
        $client = new Client();
        $query = '
        query GetCarts($idUser: Int!) {
            Kija2_Keranjang(where: {idUser: {_eq: $idUser}}) {
                idKeranjang
                idProduk
                idUser
                jumlahProduk
                totalHarga
                Produk {
                    gambarProduk
                    namaProduk
                    hargaProduk
                }
            }
        }
        ';

        try {
            $response = $client->post($this->hasura_url, [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-hasura-admin-secret' => $this->hasura_secret
                ],
                'json' => [
                    'query' => $query,
                    'variables' => ['idUser' => $idUser]
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            if (isset($data['errors'])) {
                return [];
            }

            return $data['data']['Kija2_Keranjang'];
        } catch (\Exception $e) {
            return [];
        }
    }

    public function getCartByUser($idUser)
    {
        $cart_items = $this->fetchCartsFromHasura($idUser);
        return response()->json($cart_items);
    }

    private function getMaxIdKeranjangFromHasura()
    {
        $query = '
        query GetMaxIdKeranjang {
            Kija2_Keranjang_aggregate {
                aggregate {
                    max {
                        idKeranjang
                    }
                }
            }
        }
    ';

        try {
            $client = new Client();
            $response = $client->post($this->hasura_url, [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-hasura-admin-secret' => $this->hasura_secret
                ],
                'json' => [
                    'query' => $query
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            if (isset($data['errors'])) {
                // Handle GraphQL errors
                error_log('GraphQL Errors: ' . json_encode($data['errors']));
                return null;
            }

            return $data['data']['Kija2_Keranjang_aggregate']['aggregate']['max']['idKeranjang'];
        } catch (\Exception $e) {
            // Handle exceptions
            error_log('Exception fetching max idKeranjang from Hasura: ' . $e->getMessage());
            return null;
        }
    }

    private function getProductPriceFromHasura($idProduk)
    {
        $query = '
            query GetProductPrice($idProduk: Int!) {
                Kija2_Produk_by_pk(idProduk: $idProduk) {
                    hargaProduk
                }
            }
        ';

        try {
            $client = new Client();
            $response = $client->post($this->hasura_url, [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-hasura-admin-secret' => $this->hasura_secret
                ],
                'json' => [
                    'query' => $query,
                    'variables' => ['idProduk' => $idProduk]
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            if (isset($data['errors']) || !isset($data['data']['Kija2_Produk_by_pk']['hargaProduk'])) {
                return null;
            }

            return $data['data']['Kija2_Produk_by_pk']['hargaProduk'];
        } catch (\Exception $e) {
            error_log('Exception fetching product price from Hasura: ' . $e->getMessage());
            return null;
        }
    }

    private function addProductToCart($idUser, $idProduk)
    {
        $idKeranjang = $this->getMaxIdKeranjangFromHasura();

        $idKeranjang = $idKeranjang ? $idKeranjang + 1 : 1;

        $hargaProduk = $this->getProductPriceFromHasura($idProduk);
        if ($hargaProduk === null) {
            // Jika harga produk tidak ditemukan atau terjadi kesalahan, kembalikan false
            return false;
        }


        $client = new Client();
        $mutation = '
            mutation AddProductToCart($idUser: Int!, $idProduk: Int!, $idKeranjang: Int!,  $totalHarga: Int!) {
                insert_Kija2_Keranjang_one(object: {idUser: $idUser, idProduk: $idProduk, idKeranjang: $idKeranjang, jumlahProduk: 1, totalHarga: $totalHarga}) {
                    idKeranjang
                }
            }
        ';

        try {
            $response = $client->post($this->hasura_url, [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-hasura-admin-secret' => $this->hasura_secret
                ],
                'json' => [
                    'query' => $mutation,
                    'variables' => [
                        'idUser' => (int) $idUser,
                        'idProduk' => (int) $idProduk,
                        'idKeranjang' => $idKeranjang,
                        'totalHarga' => $hargaProduk
                    ]
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            if (isset($data['errors'])) {
                // Jika terjadi kesalahan, cetak atau log pesan kesalahan
                error_log('Error adding product to cart: ' . json_encode($data['errors']));
                return false;
            }

            // Jika berhasil, Anda dapat melakukan sesuatu dengan idKeranjang baru jika perlu
            $idKeranjang = $data['data']['insert_Kija2_Keranjang_one']['idKeranjang'];
            return true;
        } catch (\Exception $e) {
            // Tangani eksepsi dan cetak atau log pesan kesalahan
            error_log('Exception adding product to cart: ' . $e->getMessage());
            return false;
        }
    }

    public function addToCart(Request $request)
    {
        $idUser = $request->input('idUser');
        $idProduk = $request->input('idProduk');

        if ($idUser && $idProduk) {
            if ($this->addProductToCart($idUser, $idProduk)) {
                return response()->json(['message' => 'Product added to cart successfully']);
            } else {
                return response()->json(['message' => 'Failed to add product to cart'], 500);
            }
        } else {
            return response()->json(['message' => 'Invalid request data'], 400);
        }
    }

    private function removeProductFromCart($idKeranjang)
    {
        $client = new Client();
        $mutation = '
        mutation RemoveProductFromCart($idKeranjang: Int!) {
            delete_Kija2_Keranjang_by_pk(idKeranjang: $idKeranjang) {
                idKeranjang
            }
        }
    ';

        try {
            // Lakukan operasi penghapusan dengan menangani hasil respons dengan lebih rinci
            $response = $client->post($this->hasura_url, [
                'headers' => [
                    'Content-Type' => 'application/json',
                    'x-hasura-admin-secret' => $this->hasura_secret
                ],
                'json' => [
                    'query' => $mutation,
                    'variables' => ['idKeranjang' => $idKeranjang]
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            if (isset($data['errors'])) {
                // Tangani kesalahan khusus
                $errorMessages = [];
                foreach ($data['errors'] as $error) {
                    $errorMessages[] = $error['message'];
                }
                error_log('Error removing product from cart: ' . json_encode($errorMessages));

                // Verifikasi jika kesalahan adalah pelanggaran kunci asing
                foreach ($errorMessages as $errorMessage) {
                    if (strpos($errorMessage, 'Foreign key violation') !== false) {
                        return false; // Gagal karena pelanggaran kunci asing
                    }
                }

                return false;
            }

            return true; // Berhasil menghapus
        } catch (\Exception $e) {
            // Tangani kesalahan umum
            error_log('Exception removing product from cart: ' . $e->getMessage());
            return false;
        }
    }

    public function deleteFromCart(Request $request)
    {
        $idKeranjang = $request->input('idKeranjang');

        if ($idKeranjang) {
            if ($this->removeProductFromCart($idKeranjang)) {
                return response()->json(['message' => 'Product removed from cart successfully']);
            } else {
                return response()->json(['message' => 'Failed to remove product from cart'], 500);
            }
        } else {
            return response()->json(['message' => 'Invalid request data'], 400);
        }
    }
}
