import requests
import json
import re
import random
import urllib.parse
import os
import sys

#####################################################################
# variables and features to send a post details request without login
#####################################################################
variables_tw_post = {
        "with_rux_injections": False,
        "includePromotedContent": True,
        "withCommunity": True,
        "withQuickPromoteEligibilityTweetFields": True,
        "withBirdwatchNotes": True,
        "withDownvotePerspective": False,
        "withReactionsMetadata": False,
        "withReactionsPerspective": False,
        "withVoice": True,
        "withV2Timeline": True
    }

features_tw_post = {
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "tweetypie_unmention_optimization_enabled": True,
        "vibe_api_enabled": False,
        "responsive_web_edit_tweet_api_enabled": False,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": False,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": False,
        "standardized_nudges_misinfo": False,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
        "interactive_text_enabled": False,
        "responsive_web_twitter_blue_verified_badge_is_enabled": True,
        "responsive_web_text_conversations_enabled": False,
        "longform_notetweets_richtext_consumption_enabled": False,
        "responsive_web_enhance_cards_enabled": False,
        "longform_notetweets_inline_media_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "responsive_web_media_download_video_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "creator_subscriptions_tweet_preview_api_enabled": True
    }

#####################################################################

class TwitterVideoScraper:

    def __init__(self):
        """ Initialize """
        
        self.headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }

        self.proxies = {
            'http': '',
            'https': '',
        }

        self.tw_regex = r'https?://(?:(?:www|m(?:obile)?)\.)?(?:twitter\.com|x\.com)/(?:(?:i/web|[^/]+)/status|statuses)/(\d+)(?:/(?:video|photo)/(\d+))?'

        self.tw_session = requests.Session()

        self.thumbnails = []
    
    def set_proxies(self, http_proxy: str, https_proxy: str) -> None:
        """ set proxy  """

        self.proxies['http'] = http_proxy 
        self.proxies['https'] = https_proxy


    def get_restid_from_tw_url(self, tw_post_url: str) -> str:
        """ get post id by url """
        try:
            rest_id = re.match(self.tw_regex, tw_post_url).group(1)
            return rest_id

        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting rest id')

    def get_guest_token(self) -> None:
        """ this method get the guest token, and set it in cookies session """

        guest_token_endpoint = 'https://api.twitter.com/1.1/guest/activate.json'
        try:
            guest_token = self.tw_session.post(guest_token_endpoint, headers=self.headers, proxies=self.proxies).json()["guest_token"]
            
            self.tw_session.cookies.set('gt', guest_token, domain='.twitter.com')

        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting guest token')


    def get_video_url_by_id_graphql(self, rest_id: str) -> tuple:
        """ this method get post details and extract video/s url 
            with best bitrate, m3u8 excluded """

        self.headers['x-guest-token'] = self.tw_session.cookies.get('gt')

        #tw_post_endpoint = "https://twitter.com/i/api/graphql/0hWvDhmW8YQ-S_ib3azIrw/TweetResultByRestId"
        tw_post_endpoint = "https://twitter.com/i/api/graphql/2ICDjqPd81tulZcYrtpTuQ/TweetResultByRestId"  #both works

        variables_tw_post['tweetId'] = rest_id

        graphql_url = f"{tw_post_endpoint}?variables={urllib.parse.quote(json.dumps(variables_tw_post))}&features={urllib.parse.quote(json.dumps(features_tw_post))}"

        # get post details
        try:
            post_details = self.tw_session.get(graphql_url, headers=self.headers, proxies=self.proxies).json()
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('connection error with api')

        # check for nsfw content, if its nsfw content change the state of nsfw attr, 
        # return becouse u need to use TwitterVideoScraperLogin class
        try:
            reason = post_details['data']['tweetResult']['result']['reason']
            if reason == 'NsfwLoggedOut':
                return [],[], True # nsfw content

        except KeyError:
            pass # sfw post

        # videos, but u have all tweet data in post_details
        try:
            all_media = post_details['data']['tweetResult']['result']['legacy']['entities']['media']
            #all_media = list(self.search_dict_key('media', post_details))[0]
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting video data from post details')

        #print(post_details)
        #exit()

        video_variants_list = []
        thumbnails = []
        for media in all_media:
            if 'video_info' in media:
                video_variants_list.append(media['video_info']['variants'])

             # thumbnails
            thumbnails.append(media['media_url_https'])

        videos_urls = []
        if video_variants_list:
            for video_variants in video_variants_list:
                video_best_bitrate = max( video_variants, key= lambda video_bitrate:video_bitrate['bitrate'] if 'bitrate' in video_bitrate else 0 ) # without m3u8
                videos_urls.append(video_best_bitrate['url'])
        else:
            raise SystemExit('video not found')

        return videos_urls, thumbnails, False


    def get_video_url_by_id_syndication(self, rest_id: str) -> list:
        """ this method get post details and extract video/s url
            this method is not used by default
            you can use it when you exceed the graphql limit """

        self.tw_session.cookies.clear()

        token = ''.join(random.choices('123456789abcdefghijklmnopqrstuvwxyz', k=10))
        syndication_url = 'https://cdn.syndication.twimg.com/tweet-result'
        params = {'id': rest_id, 'token': token,}
        headers={'user-agent': 'Googlebot'}

        try:
            post_details = self.tw_session.get(syndication_url, headers=headers, proxies=self.proxies, params=params).json()
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('connection error with api')
        
        # videos, but u have all tweet data in post_details
        try:
            all_media = post_details['mediaDetails']
        except Exception as e:
            print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
            raise SystemExit('error getting video data from details')

        video_variants_list = []
        for media in all_media:
            if 'video_info' in media:
                video_variants_list.append(media['video_info']['variants'])

        videos_urls = []
        if video_variants_list:
            for video_variants in video_variants_list:
                video_best_bitrate = max( video_variants, key= lambda video_bitrate:video_bitrate['bitrate'] if 'bitrate' in video_bitrate else 0 ) # without m3u8
                videos_urls.append(video_best_bitrate['url'])
        else:
            raise SystemExit('video not found')

        return videos_urls


    def download(self, video_url_list: list) -> list:
        """ download the video """

        downloaded_video_list = []
        for video_url in video_url_list:
            try:
                video = self.tw_session.get(video_url, headers=self.headers, proxies=self.proxies, stream=True)
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error downloading video')

            path_filename = video_url.split('?')[0].split('/')[-1]
            try:
                with open(path_filename, 'wb') as f:
                    for chunk in video.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()

                downloaded_video_list.append(path_filename)
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error writting video')

        return downloaded_video_list


    def ffmpeg_fix(self, downloaded_video_list: list) -> list:
        """ fix video to make it shareable """

        fixed_video_list = []
        for video in downloaded_video_list:
            # this is a prefix for new features
            final_video_name = f'DescargarBot_{video}'

            ffmpeg_cmd = f'ffmpeg -hide_banner -loglevel panic -y -i "{video}" -c copy "{final_video_name}"'

            try:
                # perform fix
                os.system(ffmpeg_cmd)

                # delete tmp files
                os.system(f'rm {video}')

                fixed_video_list.append(final_video_name)
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('ffmpeg error fixing video')

        return fixed_video_list


    def get_video_filesize(self, video_url_list: list) -> list:
        """ Get file size by requesting a small portion of the file """

        items_filesize = []
        for video_url in video_url_list:
            try:
                headers = self.headers.copy()
                headers.update({"Range": "bytes=0-1023"})
                video_size = self.tw_session.get(video_url, headers=headers, proxies=self.proxies)
                content_range = video_size.headers.get('Content-Range')
                if content_range:
                    total_size = int(content_range.split('/')[-1])
                    items_filesize.append(total_size / 1024 / 1024)
                    print(items_filesize)
                else:
                    print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                    raise SystemExit("Error Content-Range header missing")
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('Error getting video size')
        
        return items_filesize

    '''
    def get_video_filesize(self, video_url_list: list) -> str:
        """ get file size of requested video """

        items_filesize = []
        for video_url in video_url_list:
            try:
                video_size = self.tw_session.head(video_url, headers=self.headers, proxies=self.proxies)
                items_filesize.append(video_size.headers['content-length'])
            except Exception as e:
                print(e, "\nError on line {}".format(sys.exc_info()[-1].tb_lineno))
                raise SystemExit('error getting video size')

        return items_filesize
    '''

    '''
    def search_dict_key(self, key: str, json: dict):
        """ busca en un json (tipo lista y/o dict) por una key
            retorna el valor de el o los valores encontrados con esa key """

        for k, v in (json.items() if isinstance(json, dict) else enumerate(json) if isinstance(json, list) else []):
            if k == key:
                yield v
            elif isinstance(v, (dict, list)):
                for result in self.search_dict_key(key, v):
                    yield result
    '''

##################################################################

if __name__ == "__main__":

    # use case example

    # set x/tw video url
    tw_post_url = ''
    if tw_post_url == '':
        if len(sys.argv) < 2:
            print('you must provide a x/twitter url')
            exit()
        tw_post_url = sys.argv[1]

    # create scraper video object
    tw_video = TwitterVideoScraper()

    # set the proxy (optional, u can run it with ur own ip)
    tw_video.set_proxies('', '')

    # get post id from url
    restid = tw_video.get_restid_from_tw_url(tw_post_url)

    # get guest token, set it in cookies
    tw_video.get_guest_token()
    
    # get video url and thumbnails from video id or nsfw warning
    video_url_list, video_thumbnails, video_nsfw = tw_video.get_video_url_by_id_graphql(restid)
    #video_url_list = tw_video.get_video_url_by_id_syndication(restid)
    if video_nsfw == True:
        raise SystemExit('nsfw post, login')

    # get item filesize
    #items_filesize = tw_video.get_video_filesize(video_url_list)
    #[print('filesize: ~' + filesize + ' bytes') for filesize in items_filesize]

    # download video by url
    downloaded_video_list = tw_video.download(video_url_list)

    # fix video to make it shareable (optional, but e.g android reject the default format)
    # remember install ffmpeg to use this method
    fixed_video_list = tw_video.ffmpeg_fix(downloaded_video_list)

    tw_video.tw_session.close()
    
