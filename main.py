import os
import random
import tweepy
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.models.search_items_request import SearchItemsRequest
from paapi5_python_sdk.models.search_items_resource import SearchItemsResource
from paapi5_python_sdk.rest import ApiException

def get_amazon_product(keyword):
    """Amazonで商品を検索し、ランダムな1つの商品情報を返す"""
    
    # --- 環境変数から認証情報を取得 ---
    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    partner_tag = os.getenv("AMAZON_PARTNER_TAG")
    host = "webservices.amazon.co.jp"
    region = "us-west-2"

    # --- APIクライアントの初期化 ---
    api_client = DefaultApi(
        access_key=access_key, secret_key=secret_key, host=host, region=region
    )

    # --- 検索リクエストの作成 ---
    # 取得したい情報（リソース）を指定
    search_items_resource = [
        SearchItemsResource.ITEMINFO_TITLE,          # 商品タイトル
        SearchItemsResource.OFFERS_LISTINGS_PRICE, # 価格
        SearchItemsResource.IMAGES_PRIMARY_LARGE,    # 商品画像
        SearchItemsResource.DETAILPAGEURL,           # 商品ページURL
    ]

    try:
        # --- APIを呼び出して商品を検索 ---
        search_request = SearchItemsRequest(
            partner_tag=partner_tag,
            partner_type=PartnerType.ASSOCIATES,
            keywords=keyword,
            resources=search_items_resource,
            item_count=10, # 10件取得してランダムに1つ選ぶ
            sort_by="AvgCustomerReviews" # レビュー評価順
        )
        response = api_client.search_items(search_items_request=search_request)

        if response.search_result and response.search_result.items:
            # --- 取得した商品リストからランダムに1つ選択 ---
            product = random.choice(response.search_result.items)
            
            # --- 必要な情報を抽出 ---
            title = product.item_info.title.display_value
            url = product.detail_page_url
            price = "価格情報なし"
            if product.offers and product.offers.listings and product.offers.listings[0].price:
                price = product.offers.listings[0].price.display_amount

            return {"title": title, "url": url, "price": price}

    except ApiException as exception:
        print("Error in calling PA-API 5.0:", exception)
        return None
    except Exception as e:
        print("An unexpected error occurred:", e)
        return None


def post_to_x(product_info):
    """取得した商品情報をXに投稿する"""
    if not product_info:
        print("商品情報が取得できなかったため、投稿をスキップします。")
        return

    # --- 環境変数から認証情報を取得 ---
    api_key = os.getenv("X_API_KEY")
    api_key_secret = os.getenv("X_API_KEY_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    try:
        # --- X API v2クライアントの初期化 ---
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        # --- 投稿メッセージを作成 ---
        tweet_text = f"""
        【🤖おすすめ商品紹介】
        
        📚 {product_info['title']}
        
        💰 {product_info['price']}
        
        👇 詳しくはこちら
        {product_info['url']}
        
        #プログラミング #書籍
        """

        # --- Xに投稿 ---
        client.create_tweet(text=tweet_text)
        print("Xへの投稿に成功しました。")

    except Exception as e:
        print("Xへの投稿中にエラーが発生しました:", e)


if __name__ == "__main__":
    # --- 検索キーワード ---
    SEARCH_KEYWORD = "Python 書籍"
    
    # 1. Amazonで商品を検索
    product = get_amazon_product(SEARCH_KEYWORD)
    
    # 2. Xに投稿
    post_to_x(product)
