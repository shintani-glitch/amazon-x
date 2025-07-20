import os
import random
import tweepy
from amazon_paapi import AmazonApi

def get_amazon_product(keyword):
    """Amazonで商品を検索し、ランダムな1つの商品情報を返す"""

    # --- 環境変数から認証情報を取得 ---
    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    partner_tag = os.getenv("AMAZON_PARTNER_TAG")

    try:
        # --- APIクライアントの初期化 (国コードを'JP'に指定) ---
        # PartnerTypeはデフォルトで"Associates"のため、指定を省略
        amazon = AmazonApi(
            access_key, 
            secret_key, 
            partner_tag, 
            "JP"
        )

        # --- 商品を検索 (レビュー評価順で10件) ---
        products = amazon.search_products(
            keywords=keyword,
            item_count=10,
            sort_by="AvgCustomerReviews"
        )

        if products:
            # --- 取得した商品リストからランダムに1つ選択 ---
            product = random.choice(products)

            # --- 必要な情報を抽出 ---
            title = product.title
            url = product.url
            price = "価格情報なし"
            if product.prices and product.prices.display_amount:
                price = product.prices.display_amount

            return {"title": title, "url": url, "price": price}

    except Exception as e:
        print(f"Amazon APIの呼び出し中にエラーが発生しました: {e}")
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
        client.create_tweet(text=tweet_text.strip())
        print("Xへの投稿に成功しました。")

    except Exception as e:
        print(f"Xへの投稿中にエラーが発生しました: {e}")


if __name__ == "__main__":
    # --- 検索キーワード ---
    SEARCH_KEYWORD = "Python 書籍"

    # 1. Amazonで商品を検索
    product = get_amazon_product(SEARCH_KEYWORD)

    # 2. Xに投稿
    post_to_x(product)
