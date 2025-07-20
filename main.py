import os
import random
import tweepy
from amazon_paapi import AmazonApi

def get_amazon_product(keyword):
    """Amazonで商品を検索し、ランダムな1つの商品情報を返す"""
    
    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    partner_tag = os.getenv("AMAZON_PARTNER_TAG")
    
    try:
        # 【最重要修正点】
        # 取得したい情報（リソース）のリストをここで定義し、
        # AmazonApiオブジェクトの初期化時に渡します。
        search_resources = [
            "ItemInfo.Title",
            "DetailPageURL",
            "Offers.Listings.Price"
        ]

        amazon = AmazonApi(
            access_key, 
            secret_key, 
            partner_tag, 
            "JP",
            resources=search_resources # <- resourcesはここで指定します
        )

        # こちらのsearch_itemsからは、resourcesの指定を削除します
        search_result = amazon.search_items(
            keywords=keyword,
            item_count=10,
            sort_by="AvgCustomerReviews"
        )

        if search_result and search_result.items:
            product = random.choice(search_result.items)
            
            title = product.title
            url = product.url
            price = "価格情報なし"
            if product.prices and product.prices.display_amount:
                price = product.prices.display_amount

            return {"title": title, "url": url, "price": price}

    except Exception as e:
        print(f"Amazon APIの呼び出し中に予期せぬエラーが発生しました: {type(e).__name__} - {e}")
        return None

    print("Amazonで対象の商品が見つかりませんでした。")
    return None


def post_to_x(product_info):
    """取得した商品情報をXに投稿する"""
    if not product_info:
        print("商品情報が取得できなかったため、投稿をスキップします。")
        return

    api_key = os.getenv("X_API_KEY")
    api_key_secret = os.getenv("X_API_KEY_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )

        tweet_text = f"""
        【🤖おすすめ商品紹介】
        
        📚 {product_info['title']}
        
        💰 {product_info['price']}
        
        👇 詳しくはこちら
        {product_info['url']}
        
        #プログラミング #書籍
        """

        client.create_tweet(text=tweet_text.strip())
        print("Xへの投稿に成功しました。")

    except Exception as e:
        print(f"Xへの投稿中にエラーが発生しました: {e}")


if __name__ == "__main__":
    SEARCH_KEYWORD = "Python 書籍"
    
    print(f"「{SEARCH_KEYWORD}」のキーワードで商品検索を開始します...")
    product = get_amazon_product(SEARCH_KEYWORD)
    
    if product:
        print(f"取得した商品: {product['title']}")
        print("Xへの投稿を開始します...")
        post_to_x(product)
    else:
        print("投稿する商品が見つからなかったため、処理を終了します。")
