# ghost-iota-pay
Pay per content in ghost blog with IOTA

![How it should work](./flowchart.svg)

## Running ghost-iota-pay
### Install requirements
```shell
pip install -r requirements.txt
```

### Set environment variables
Copy the env file  
```shell
cp example.env .env
```
Alter the following variables:  

- `URL`
  Default Value: `http://localhost:2365` . Set to the url of the ghost blog which shall be fetched.

- `GHOST_ADMIN_KEY`
  Default Value: _null_. Set to the admin key of a custom integration. Can be generated in the admin dashboard ([Custom Integration](https://ghost.org/integrations/custom-integrations/))

- `IOTA_ADDRESS`
  Default Value: _null_. Set to the IOTA Address which is owned by the blog. The application will listen there for incoming payments.

- `NODE_URL`
  Default Value: `https://api.hornet-1.testnet.chrysalis2.com`. Set to the url of your prefered node.  
  :warning: **This is the DEV-Net. If you want to use the mainnet you should use mainnet nodes such as `https://chrysalis-nodes.iota.org`**


### Run the app
```shell
python -m flask run
```
This will serve the app on port 5000.

## Usage
When offering payed articles on your ghost blog just add a link on the subscribtion form which points to `https://your-ghost-iota-pay-domain.com/{slug}` where slug is the slug of the requested article.
After the payment the article is fetched through the admin API and served to the user.
