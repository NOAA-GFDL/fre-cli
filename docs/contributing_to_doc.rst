contributing_to_doc
================================================

How to Contribute to ``fre-cli``'s documentation
------------------------------------------------

* Fork fre-cli on github
* On github, navigate to your fre-cli fork, and click “settings”
* In “settings”, click “pages”
* In “pages”, under “build and deployment”, make sure “source” is set to “Deploy from a branch”
* Under that, find “Branch”, make sure the branch selected is “gh-pages”. 
* The branch “gh-pages” is “automagic”- i.e. do not change anything about it nor create a new one,
  nor interact with anything in that branch directly.
* Back on top where you found “settings”, find and click “actions” to the left
* Enable running the workflow actions assoc with the fre-cli repo under “.github/workflows”
* The documentation builds as the last steps to create_test_conda_env.yml when theres a push to main.
  To get your first workflow run on your fork, comment out the “github.ref == ‘refs/heads/main’” bit
  so that it runs when you push to any branch, and make a small, trivial, commit somewhere to your
  remote fork. 
* You should be able to find the deployed webpage from a successful workflow at
  https://your_username.github.io/fre-cli (if you did not change the fork’s name from fre-cli, that is).
* Ian’s is at https://ilaflott.github.io/ians_fre_cli/ 
* If you’re only editing docs, you can make the turn-around time on your workflow ~3 min faster by
  commenting-out the pylint and pytest steps in create_test_conda_env.yml, and disable running the
  build_conda,yml workflow



