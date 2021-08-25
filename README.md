<p align="center">
    <img src="https://raw.githubusercontent.com/F-Node-Karlsruhe/ghost-iota-pay/main/static/logo.png" width="140px" alt="ghost-iota-pay" />
</p>  

# ghost-iota-pay
[![Docker](https://img.shields.io/docker/pulls/fnode/ghost-iota-pay.svg)](https://hub.docker.com/r/fnode/ghost-iota-pay/)
[![Docker](https://img.shields.io/docker/stars/fnode/ghost-iota-pay.svg)](https://hub.docker.com/r/fnode/ghost-iota-pay/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/F-Node-Karlsruhe/ghost-iota-pay/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/F-Node-Karlsruhe/ghost-iota-pay.svg)](https://github.com/F-Node-Karlsruhe/ghost-iota-pay/issues)  
**Pay per content in ghost blog with [IOTA](https://www.iota.org/)**  

Test it here: [blog.f-node.de](https://blog.f-node.de)  
Watch it here: [https://www.youtube.com/watch?v=3XG2W9J3b1A](https://www.youtube.com/watch?v=3XG2W9J3b1A)  
Or use the service of [https://pay-per-content.com](https://pay-per-content.com)  

![How it works](https://raw.githubusercontent.com/F-Node-Karlsruhe/ghost-iota-pay/main/images/flowchart.svg)

## Running ghost-iota-pay
### Install requirements
```shell
pip install -r requirements.txt
```
If python does not find the iota client install it from the wheel file
```shell
pip install iota_client_python-0.2.0_alpha.3-cp36-abi3-linux_x86_64.whl
``` 

### Set environment variables
Copy the `.env` file  
```shell
cp example.env .env
```
Alter the following variables in the `.env` file:  

- `URL`
  Default Value: `http://localhost:2368` . Set to the url of the ghost blog which shall be fetched.

- `GHOST_ADMIN_KEY`
  Default Value: _null_. Set to the admin key of a custom integration. Can be generated in the admin dashboard ([Custom Integration](https://ghost.org/integrations/custom-integrations/))

- `DEFAULT_IOTA_ADDRESS`
  Default Value: `NO ADDRESS GIVEN`. Set to the IOTA Address which is owned by the blog. The application will listen there for incoming payments.

- `NODE_URL`
  Default Value: `https://api.hornet-1.testnet.chrysalis2.com`. Set to the url of your prefered node.  
  :warning: **This is the DEV-Net. If you want to use the mainnet you should use mainnet nodes such as `https://chrysalis-nodes.iota.org`**


### Run the app
```shell
python app.py
```
This will serve the app on port 5000.

## Run ghost-iota-pay with Docker
### Build and run ghost-iota-pay with Docker

**Make sure that the [.env](#set-environment-variables) file exists**

Build the image
```shell
docker build --tag ghost-iota-pay .
```

Run the image as container
```shell
docker run -it -p 5000:5000 -v /$(pwd)/data:/app/data --env-file .env ghost-iota-pay
```

### Run ghost-iota-pay with Docker from repository

**Make sure that the [.env](#set-environment-variables) file exists**

Run image from repository
```shell
docker run -it -p 5000:5000 -v /$(pwd)/data:/app/data --env-file .env fnode/ghost-iota-pay
```

### Run ghost-iota-pay with docker-compose

**Make sure that the [.env](#set-environment-variables) file exists**

Run image from repository
```shell
docker-compose up
```

This will serve the app on port 5000.

## Usage
When offering payed articles on your ghost blog just add a link on the subscribtion form which points to `https://your-ghost-iota-pay-domain.com/{{slug}}` where slug is the slug of the requested article.
After the payment the article is fetched through the admin API and served to the user.  

## Integration in ghost
Put the following code into the `post.hbs` of your ghost theme and replace `{{ghost-iota-pay-url}}` with the url of your ghost-iota-pay gateway:  
```handlebars
{{#has visibility="paid"}}
    <button id="ghost-iota-pay-link" 
        style="
            margin-left: 15px;
            background: black;
            border-radius: 5px;">
                <a style="color: white;" 
                    href="{{ghost-iota-pay-url}}{{slug}}">
                        Buy with 
                        <img style="
                            display: inline-block;
                            height:25px;
                            margin-top: -6px;" 
                            src="https://www.iota.org/logo-icon-light.svg"
                            alt="IOTA"/>
                </a>
   </button>
{{/has}}
```
Example file [ghost-integration/post.hbs](ghost-integration/post.hbs)

## Author address setup
You can set `AUTHOR_ADDRESSES=true` in your `.env` file to allow authors to get paid individually.
If so, the authors can paste in their current IOTA address in the `location` field in their ghost admin panel.  
When an article is requested, the ghost API is fetched to get the latest address. If there is none, there is a fallback to the last address used or if this is not the case, the default address specified in the `.env` file is used.  

**Improvement**
As an IOTA address is quite ugly in the location field of the author, you can modify you theme in the `author.hbs` like so, using [IOTA Buttons](https://iota-button.org):

```handlebars
{{#if location}}
    <span class="author-profile-location">
        <iota-button address="{{location}}"
                      currency="EUR"
                      label="Donate"
                      merchant="Author"
                      type="donation">
        </iota-button></span>
{{/if}}
```

## Admin panel setup
You can set `ADMIN_PANEL=true` in your `.env` file to enable the admin panel on the `/admin` path.  
The admin panel is secured using basic authentication which credentials are specified in the `.env` file as well.


## Donation

I develop this gateway in my free time. If you want to support me or if my work helps you, kindly consider a small donation :)

[<img src="https://img.shields.io/badge/iota1qrkale2wq836sxm2y5kkv58lt7x3w3m3dwk6zztfyv4h3tujs9fhv4ru4wc-lightgrey?style=social&logo=iota" alt="IOTA">](https://blog.f-node.de/author/f-node/)
