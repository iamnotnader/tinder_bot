
[[ -s "$HOME/.profile" ]] && source "$HOME/.profile" # Load the default .profile

[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*

if [[ -s $HOME/.rvm/scripts/rvm ]]; then
  source $HOME/.rvm/scripts/rvm;
fi

alias gametime='source ~/Development/virtual_envs/django_tutorial/bin/activate'

VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python
source /usr/local/bin/virtualenvwrapper.sh

alias start='sudo pkill mongod; sudo mongod &'
alias bf='cd ~/Development/biddie_frontend; workon biddie_frontend; s'
alias bb='cd ~/Development/biddie_backend; workon biddie_backend;'
alias rs='cd ~/Development/biddie_backend; python manage.py runserver;'
alias es='cd ~/Development/biddie_frontend; ember serve;'
alias et='cd ~/Development/biddie_frontend; ember test;'
alias etf='cd ~/Development/biddie_frontend; ember test --filter '
alias s='source ~/Development/biddie_frontend/.bash_profile;'
alias v='vim'
alias ll='ls -la'

alias g='git'
alias ga='git add'
alias gap='git add -p'
alias gs='git status'
alias gd='git diff'
alias gco='git checkout'
alias gc='git commit'
alias gcm="git commit -m"
alias gl='git log'
alias gp='git push'
alias gph='git push heroku master'
alias gss='git stash save'
alias gsa='git stash apply'

alias rpg='pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start'
alias vbp='vim ~/.bash_profile'
alias f='sudo python ~/Development/biddie_backend/runserver.py'
alias m='sudo mongod'

alias temp='workon interview_question; cd ~/Development/tmp/flaskr/'

alias bb_prod="ssh -i ~/Dropbox/small_folder/aws_keys/biddie_1.cer ubuntu@ec2-54-148-224-22.us-west-2.compute.amazonaws.com"
alias bf_prod="ssh -i ~/Dropbox/small_folder/aws_keys/biddie_1.cer ubuntu@ec2-54-148-102-223.us-west-2.compute.amazonaws.com"
alias interview_test="ssh -i ~/Dropbox/small_folder/aws_keys/biddie_1.cer ubuntu@ec2-54-149-109-115.us-west-2.compute.amazonaws.com"
alias deploy_bf="cd ~/Development/biddie_frontend; ember build --environment production; ./deploy_to_s3 "

# avoid duplicates..
export HISTCONTROL=ignoredups:erasedups

# append history entries..
shopt -s histappend

# After each command, save and reload history
export PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"

export DEBUG=True
alias npm-exec='PATH=$(npm bin):$PATH'
export PATH=$(npm bin):$PATH
