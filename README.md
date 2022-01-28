# gitlab-mr-url
CLI utility to get the URL of the Gitlab merge request that introduced a given commit.

# Setup

1. Install `python-gitlab`:
```
sudo pip install --upgrade python-gitlab
```

2. Go to Gitlab -> Preferences -> Private Access Token -> Generate PAT
and generate a read token.
3. In order to access your Gitlab instance, 3 environment variables are required:
- `GITLAB_URL`: URL of your Gitlab instance, e.g. `https://gitlab.com`  if using gitlab.com.
- `GITLAB_TOKEN`: the access token generated in step #2.
- `GITLAB_PROJECT_ID`: your project's ID, to get it simply go to your project main page. The project ID is indicated right below the project's name and icon at the top.

All done!
You can now use `glab.py`! 🥳!

# Usage

## Get MR URL from commit ID
`./glab.py <some commit id>`
returns the MR containing this commit

The commit id need to be complete, as exact match is required for now.

## Generate cache
To make this more efficient, you can fetch a large number (about 1200) of MRs and cache them by using:
`./glab.py gen`

This will generate a map of commit id -> MR url in `commit_mr.json`.


# IDE Integration

This project was made for integrating it into an IDE via the following steps:

1. Get the commit id for the current line with e.g:
```lua
"git --no-pager log -L" .. line_number .. ",+1:'" .. path .. "' --pretty=format:'%H'"
```

2. Get the merge request URL by running:
`/path/to/glab.py <commit id>`

3. Display the URL, or open it directly in your browser.

