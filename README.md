# x / twitter video scraper
<div align="center">
  
![DescargarBot](https://www.descargarbot.com/v/download-github_twitter.png)
  
[![Reddit](https://img.shields.io/badge/on-descargarbot?logo=github&label=status&color=green
)](https://github.com/descargarbot/twitter-video-scraper/issues "Twitter")
</div>

<h2>dependencies</h2>
<code>Python 3.9+</code>
<code>requests</code>
<code>FFmpeg</code>
<br>
<br>
<h2>install dependencies</h2>
<ul>
<li><h3>requests</h3></li>
  <code>pip install requests</code><br>
  <code>pip install -U 'requests[socks]'</code>
  <br>
<li> <h3>FFmpeg </h3></li>
  <ul>
  <li> <h3> Linux </h3> </li>
  <code> sudo apt install ffmpeg </code>
  <li> <h3>MacOS</h3> </li>
    you can use this <a href="https://bbc.github.io/bbcat-orchestration-docs/installation-mac-manual/" > tutorial</a>
  <li> <h3>Windows</h3> </li>
    you can use this <a href="https://www.wikihow.com/Install-FFmpeg-on-Windows" > tutorial</a>
  </ul>
<br>
</ul>
<h2>use case example</h2>

    #import the class TwitterVideoScraper
    from twitter_video_scraper import TwitterVideoScraper
    
    # set x/tw video url
    tw_post_url = "your x/twitter video post"

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
    
  > [!NOTE]\
  > you can use the CLI
  <br><br>
  > <code>python3 twitter_video_scraper.py TWITTER_URL</code>
  
<br><br>
<h2>online</h2>
<ul>
  ⤵
  <li> web 🤖 <a href="https://descargarbot.com" >  DescargarBot.com</a></li>
  <li> <a href="https://t.me/xDescargarBot" > Telegram Bot 🤖 </a></li>
  <li> <a href="https://discord.gg/gcFVruyjeQ" > Discord Bot 🤖 </a></li>
</ul>

