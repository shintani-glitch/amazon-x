import os
import random
import boto3
import tweepy
from botocore.exceptions import ClientError

def get_amazon_product(keyword):
    """boto3を使い、Amazonで商品を検索して商品情報を返す"""
    
    # --- 環境変数から認証情報を取得 ---
    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    partner_tag = os.getenv("AMAZON_PARTNER_TAG")
    
    # PA-API v5 のサービス名とリージョンを指定
    service_name = "paapi5"
    # 日本のマーケットプレイスの場合、リージョンは "us-west-2"
    region_name = "us-west-2" 

    try:
        # --- boto3 クライアントの作成 ---
        client = boto3.client(
            service_name,
            region_name=region_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        
        # --- APIに渡す検索パラメータを定義 ---
        response = client.search_items(
            PartnerTag=partner_tag,
            PartnerType="Associates",
            Keywords=keyword,
            ItemCount=10,
            SortBy="AvgCustomerReviews",
            Resources=[
                "ItemInfo.Title",
                "DetailPageURL",
ax               "Offers.Listings.Price"
            ]
        )

        # --- 応答（辞書）から商品リストを取得 ---
        items = response.get('SearchResult', {}).get('Items', [])
        
        if items:
            # --- ランダムに商品を1つ選択 ---
            product_data = random.choice(items)
            
            # --- 辞書の階層をたどって、安全に情報を抽出 ---
            title = product_data.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', 'タイトル情報なし')
            url = product_data.get('DetailPageURL', '#')
            
            price = "価格情報なし"
            # 価格情報は階層が深いので、特に慎重にチェック
            if 'Offers' in product_data and product_data['Offers'].get('Listings'):
                price = product_data['Offers']['Listings'][0].get('Price', {}).get('DisplayAmount', '価格情報なし')

            return {"title": title, "url": url, "price": price}

    except ClientError as e:
        # boto3が返すAPIエラーを捕捉
        print(f"boto3からAPIエラーが返されました: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {type(e).__name__} - {e}")
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
