# **GIT HOWTO**

### ***Merge one local branch into another local branch:***

1. Switch to branch "dev":<br>
   `git checkout dev`
2. Merge branch "angie_brunch" into "dev":<br>
   `git merge angie_branch`

### ***Delete branch locally and remotely:***
- Delete branch locally:<br>
`git branch -d localBranchName`
- Delete branch remotely:<br>
`git push origin --delete remoteBranchName`
### ***If there are any problems: 😄 ***
check the state of the repository first: `git status`
