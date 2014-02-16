import praw

r = praw.Reddit(user_agent='pugsmakemehappy')
submissions = r.get_subreddit('Puggifs').get_new(limit=None)
print [x.url for x in submissions]
