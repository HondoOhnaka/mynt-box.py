# mynt-box.py #

A script to automatically generate a mynt blog from files hosted on your [Dropbox](http://dropbox.com) and edited solely on a mobile device, in my case, with [Byword](http://bywordapp.com/) on the iPhone.

I like blogging, Python, automation, Dropbox and fun problems. Why not combine them?

## Prologue ##

I took ideas for this from several locations:

1. Dropbox Synced - [Second Crack](https://github.com/marcoarment/secondcrack), [Marco Arment's](http://marco.org) static blog engine.  He had written an entire static blog engine in PHP using the CLI/daemon version of dropbox.  Great idea, __except__ that my host is shared and they don't allow daemon processes, like Dropbox, to run on their servers. (Strike one)

I wanted this to run automatically. It seems my solution was doing something as a cron job. Given the shared hosting situation, I can run a cron every 5 minutes. Not the instant update I was hoping for, but I can accept it for now until I can afford a VPS for my little blog.

## Tools ##

1. [Mynt](http://mynt.mirroredwhite.com/) - a static blog engine. There are many out there, I chose it because a) it's written in Python and b) I know Python better than Ruby. I am also familiar with the default template engine, Jinja. There also may be 
some personal reason that I need to sort out.
1. [Byword](http://bywordapp.com/) to edit the blog posts. Configure it to drop your files into _posts directory on the server where you are going to run Mynt.
1. [Dropbox](http://dropbox.com) to host the files and act as a middle ground between the webserver and your mobile device.  I would have used a FTP-based file editor if there was one that worked as well as Byword. 

## Configuration ##

Since this script was specific to my setup there are some naughty hard-coded paths that you will want to change.  

First: Put in your app keys from your Dropbox account:

    APP_KEY = '<YOUR DROPBOX KEY>'
    APP_SECRET = '<YOUR DROPBOX SECRET KEY>'
    
Second, set how many minutes back you want to check for changes. The shortest interval I can run this script is every 5 minutes so I set it to check for any changes since the previous run.
     
    TIME_INTERVAL = 5 # minutes
    
Embarrassingly, I have not done much with the datetime module prior to this, so some of my configs for this are a bit kludgy. 

I think the fixes for these are rather trivial, but for now these are part of my config. \[Feel free to submit the fixes for these.\] ;)

    TZ_OFFSET = 6 
    SERVER_TZ_OFFSET = 0 # difference between my time and the server, may not be needed

Set `debug = True` if you want some verbosity to track down errors.

The last line in the script is the one with the most hard-codery.  

    subprocess.call(['/path/to/your/bin/mynt', 'gen', '-f', '/path/to/your/blog/directory', '/path/to/public/html/directory/'])
    
Change it to match your locations and run as needed. Attach to a cron job to execute at some interval to pull your files down and run the mynt cli generator.  

## Execution ##

### Manually ###

Make it executable: `chmod 0755 mynt-box.py`

Execute:
    
    ./mynt-box.py <dropbox path> <local path>
    
If this is the first time you run the script, you'll need to authorize the
"application" by visiting a url provided by Dropbox.  So you'll probably want to run in manually the first time.  

It stores the access token locally and, once set, won't bother you for it again.

### Automated via crontab ###

Add a cron entry for it to run as needed. For me, I run it every 5 minutes, so it looks like:

	*/5 * * * * /path/to/home-dir/my_scripts/dbget.py _posts /path/to/your/blog/_posts >/dev/null 2>&1
	
I added the clause on the end to send email notifications to the "trash". Rather than get status messages every five minutes.
	

## Epilogue ##

If there is any interest I may make this a bit more robust and less custom to my own needs.