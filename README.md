# Tokopedia Scraper

## Usage

### Single Shop Scraping

```bash
scraper shop --shop-username shop-username --page 2
scraper --headless shop --shop-username shop-username --page 3
```

### Batch Shop Scraping

**Cara 1: Menggunakan Input File**

Buat file `shops.txt` dengan format:

```
# Format: username,page
balibudalife,2
amore-collections,3
example-shop,1
```

Jalankan:

```bash
scraper batch-shop --input-file shops.txt
scraper --headless batch-shop --input-file data/inputs/shops.txt --page 5
```

**Cara 2: Command Line Arguments**

```bash
scraper batch-shop --shop-usernames balibudalife amore-collections example-shop --page 2
```

### Single Product Image Scraping

```bash
scraper image --product-url "https://www.tokopedia.com/product-url"
```

### Batch Product Image Scraping

**Cara 1: Menggunakan Input File**

Buat file `shops.txt` dengan format:

```
https://www.tokopedia.com/product1
https://www.tokopedia.com/product2
https://www.tokopedia.com/product3
```

Jalankan:

```bash
scraper batch --input-file product_urls.txt
scraper --headless batch --input-file product_urls.txt
```

**Cara 2: Command Line Arguments**

```bash
scraper batch --product-urls "url1" "url2" "url3"
```

## Disclaimer

Tool ini hanya untuk keperluan edukasi. Dimohon untuk mematuhi kebijakan dari Tokopedia.
