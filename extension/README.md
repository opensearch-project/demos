## OpenSearch Demos VS Code Extension

This directory contains a small Visual Studio Code extension that enables a better user experience when OpenSearch loads in the GitPod environment. When running in GitPod, the extension is built and installed automatically with the scripts in `.gitpod.yml`.

### What does this extension do?

When this extension is loaded, it starts a VS Code webview and displays a built-in message that OpenSearch is loading (_Please wait while OpenSearch is loading._) and then waits for the presence of `ready.txt`. Once `ready.txt` exists the webview automatically updates to indicate that OpenSearch is ready (_OpenSearch is Ready!_).

If `/html/loading.html` and `/html/ready.html` are both detected when the extension starts, it will load these files instead of the built-in messages.

### Why is this needed?

OpenSearch has an unusual cold start sequence: OpenSearch starts, then OpenSearch Dashboards. While OpenSearch Dashboards is initializing, attempting to access the web UI will display  "OpenSearch Dashboards is not ready" for many seconds. In a production environment, you don't start OpenSearch Dashboards very often - a user is unlikely to see this message. In a demo environment when you're trying to get going rapidly from a cold start, this is a frustrating experience with no instructions on what to do next.

In the GitPod environment, there is a shell script that is trigger upon the Dashboard's port (5601) becoming available. The shell script polls 5061 and evaluates if the response contains the not ready message. When the message goes away (e.g. OpenSearch Dashboards is responding with its UI), it touches the file `ready.txt`. 

GitPod is based on a remote VS Code instance and can load extensions. This extension provides a way to add a friendly message that smooths over the odd cold start process. Additionally, because webviews aren't sandboxed (compared to VS Code previews) links can spawn new browser windows without a pop-up warning.

### Do I need to use this if I'm on local Docker?

Nope! This really only useful in GitPod, but if you find a way to use it - go for it!