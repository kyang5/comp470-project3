#!/usr/bin/env python
# coding: utf-8

# In[86]:


from github import Github
import pandas as pd
import matplotlib.pyplot as plt

g = Github("access_token")


# In[87]:


repo = g.get_repo("wesnoth/wesnoth")


# In[130]:


import numpy as np
import datetime

issues = repo.get_issues(state='all')

title_array = []
num_array = []
state_array = []
created_array = []
closed_array = []
issue_label_array = []
issue_assignees_array = []
issue_comments_array = []
issue_locked_array = []

count_array = []
for issue in issues:
    count_array.append(1)
    title_array.append(issue.title)
    num_array.append(issue.number)
    state_array.append(issue.state)
    created_array.append(issue.created_at)
    closed_array.append(issue.closed_at)
    
    
    label_array = []

    for label in issue.labels:
        label_array.append(label.name)
    issue_label_array.append(label_array)
    
    assignee_count = 0
    for assignee in issue.assignees:
        assignee_count = assignee_count + 1
    issue_assignees_array.append(assignee_count)
    
    issue_comments_array.append(issue.comments)
    
    issue_locked_array.append(issue.locked)


# In[37]:


df = pd.DataFrame()

df['state'] = np.array(state_array).tolist()
df['number'] = np.array(num_array).tolist()
df['title'] = np.array(title_array).tolist()
df['label'] =  np.array(issue_label_array).tolist()
df['created'] = np.array(created_array).tolist()
df['closed'] = np.array(closed_array).tolist()
df['assignee count'] =  np.array(issue_assignees_array).tolist()
df['comments'] = np.array(issue_comments_array).tolist()
df['locked'] = np.array(issue_locked_array).tolist()


# In[131]:


df.created = pd.to_datetime(df.created)
df.closed = pd.to_datetime(df.closed)


# In[39]:


open_y_m = df[df["state"].str.contains('open')].groupby([df['created'].dt.year, df['created'].dt.month]).agg({'count'})
closed_y_m = df[df["state"].str.contains('closed')].groupby([df['created'].dt.year, df['created'].dt.month]).agg({'count'})
ax = open_y_m['state'].plot(legend=False,title = "Created Issues w/ Open Status by Year, Month Created")
ax.set_xlabel("year, month")
ax.set_ylabel("number of issues")
ax = closed_y_m['state'].plot(legend=False,title = "Created Issues w/ Closed Status by Year, Month")
ax.set_xlabel("year, month")
ax.set_ylabel("count")


# In[442]:


df['days open'] = (df['closed'] - df['created']).dt.days


# In[443]:


closed_assignee = df[df["state"].str.contains('closed')]
plt.scatter(closed_assignee['days open'], closed_assignee['assignee count'])
plt.title("Number of Assignee VS Days Issue Open")
plt.xlabel("days open")
plt.ylabel("assignee(s)")
plt.show()


# In[444]:


closed_comments = df[df["state"].str.contains('closed')]
plt.scatter(closed_assignee['days open'], closed_assignee['comments'])
plt.title("Number of Comment VS Days Issue Open")
plt.xlabel("days open")
plt.ylabel("comment(s)")
plt.show()


# In[84]:


##Stage 2: Commits
commit_array = []
commit_committer_array = []
commit_date_array = []
commit_tree_array = []
commit_url_array = []

commits = repo.get_commits()
for commit in commits:
    
    ##add the sha value into the array
    commit_array.append(commit.sha[0:6])
    
    ##add the commiter into the array
    commit_committer_array.append(commit.commit.author.name)
    
    ##add the date of commit into the array
    commit_date_array.append(str(commit.commit.author.date))
    
    ##add the tree of commit into the array
    commit_tree_array.append(commit.commit.tree.sha[0:6])
    
    ##add the url of the commit into the array
    commit_url_array.append(commit.commit.url)


# In[88]:


commits = pd.DataFrame()

commits['commit'] = np.array(commit_array).tolist()
commits['committer'] = np.array(commit_committer_array).tolist()
commits['date'] = np.array(commit_date_array).tolist()
commits['tree'] =  np.array(commit_tree_array).tolist()
commits['url'] = np.array(commit_url_array).tolist()


# In[43]:


commit_group = commits["commit"].groupby([commits['date'].dt.year, commits['date'].dt.month]).agg({'count'})
commits.date = pd.to_datetime(commits.date)


# In[48]:


ax = commit_group.plot(legend=False, title = "Number of Commits by Year, Month")
ax.set_xlabel("year, month")
ax.set_ylabel("number of commits")


# In[51]:


##Stage 3: Code Size AND THIS PROPERLY WORKS WTF
code_size_array=[]
path_array=[]
date_array=[]

##limiter
limiter=0
limit=1

commits=repo.get_commits() ##new attempt, can traverse through nested trees
for commit in commits[::50]: ##change the number to iterate every nth element
    code_size=0
    commit_path_array=[]
    initial_tree=repo.get_git_tree(commit.commit.tree.sha,recursive=True)
    for item in initial_tree.tree:
        if item.type=='blob':
            code_size+=item.size
            commit_path_array.append(str(item.path))
            
    ##add code size, path, and date to their respective arrays
    code_size_array.append(code_size)
    path_array.append(commit_path_array)
    date_array.append(str(commit.commit.author.date))
    #print(code_size_array)
    #print(date_array)

    ##limiter    
    limit += 1
    if limit==limiter:
        #print(code_size)
        break
        
#print(code_size_array)


# In[77]:


codeSize = pd.DataFrame()

codeSize['date'] = np.array(date_array).tolist()
codeSize['size'] = np.array(code_size_array).tolist()
codeSize['path'] = np.array(path_array).tolist()
codeSize


# In[111]:


codeSize.date = pd.to_datetime(codeSize.date)

size_group = codeSize["size"].groupby([codeSize['date'].dt.year, codeSize['date'].dt.month]).agg({'sum'})

# In[102]:


size_group


# In[104]:


# stage 3 graph
ax1 = size_group.plot(title = "Code Size by Year, Month")
ax1.legend(["size"])
ax1.set_xlabel("year, month")
ax1.set_ylabel("size")


# In[103]:


ax2 = issues_group.plot(title = "Issues by Year, Month")
ax2.legend(["issues"])
ax2.set_xlabel("year, month")
ax2.set_ylabel("number of issues")


# In[186]:


# stage 4
codeSize = pd.DataFrame()

codeSize['date'] = np.array(date_array).tolist()
codeSize['size'] = np.array(code_size_array).tolist()
codeSize.date = pd.to_datetime(codeSize.date)


# In[193]:


codeSize['norm_date'] = codeSize['date'].dt.normalize()


# In[190]:


issues = pd.DataFrame()

issues['date'] = np.array(created_array).tolist()
issues['count'] = np.array(count_array).tolist()
issues['norm_date'] = issues['date'].dt.normalize()


# In[213]:


out = issues.merge(codeSize, on='norm_date', how='left')


# In[211]:


out['issue_density'] = out['count']/out['size']
out
issue_density = out['issue_density'].groupby([out['norm_date'].dt.year, out['norm_date'].dt.month]).agg({'sum'})


# In[212]:


ax1 = issue_density.plot(title = "Issues Density by Year, Month")
ax1.legend(["issue density"])
ax1.set_xlabel("year, month")
ax1.set_ylabel("issue/code size")


# In[ ]:




