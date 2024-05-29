const express = require('express');
const axios = require('axios');
const app = express();

const HASURA_API_URL = 'https://flying-dingo-28.hasura.app/v1/graphql';
const HASURA_API_KEY = 'VMk2qKcMIReoIA5H82r0JX6XE2OGJ442lPPdyjDfHmnx6Dg3VTs8T52kxENOOKUV';

const fetchProductsFromHasura = async () => {
    const query = `
        query GetProducts {
            Kija2_Produk {
                idProduk
                namaProduk
                hargaProduk
                stokProduk
                gambarProduk
            }
        }
    `;
    
    try {
        const response = await axios.post(HASURA_API_URL, { query }, {
            headers: {
                'Content-Type': 'application/json',
                'x-hasura-admin-secret': HASURA_API_KEY
            }
        });

        if (response.data.errors) {
            console.error('GraphQL Errors:', response.data.errors);
            return [];
        }

        return response.data.data.Kija2_Produk;
    } catch (error) {
        if (error.response) {
            console.error('Error fetching products from Hasura:', error.response.data);
        } else {
            console.error('Error fetching products from Hasura:', error.message);
        }
        return [];
    }
};

app.get('/products', async (req, res) => {
    const products = await fetchProductsFromHasura();
    res.json(products);
});

app.get('/products/:idProduk', async (req, res) => {
    const productId = parseInt(req.params.idProduk);
    const products = await fetchProductsFromHasura();
    const product = products.find(product => product.idProduk === productId);

    if (product) {
        res.json(product);
    } else {
        res.status(404).json({ error: "Product not found" });
    }
});

app.listen(5000, () => {
    console.log("Server Running on port 5000");
});
