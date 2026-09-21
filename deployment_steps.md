# How to Deploy RAHAT Dashboard Manually

If the public tunnel drops or you need to restart the project manually on your own machine, follow these two simple steps. You will need to open **two separate terminal (or command prompt) windows** in your `d:\flood` project folder.

## Step 1: Start the Local Dashboard Server

In your **first** terminal window, run the lightweight Python server. This serves the dashboard locally on port 3000.

```bash
python run_server.py
```
*(Leave this terminal window open and running. Your dashboard is now live locally at `http://localhost:3000`)*

## Step 2: Create the Public Tunnel (Serveo)

In your **second** terminal window, run the following exact SSH command. This will tunnel your local port 3000 to the public web safely so anyone can access it over the internet.

```bash
ssh -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -R 80:127.0.0.1:3000 serveo.net
```
*(Leave this terminal window open as well)*

### Finding Your Live URL

As soon as you run the second command, it will print out a line saying something like:
`Forwarding HTTP traffic from https://[random-string].serveousercontent.com`

**That link is your brand new, live public URL!** You can copy and share it immediately. 

*(Note: Serveo might show a quick security warning page on the first visit since it's a free tunneling service—just click "Continue" or "Proceed" to get to the dashboard).*

### Troubleshooting

If the tunnel ever times out during your presentation:
1. Go to that second terminal window.
2. Press `Ctrl+C` to stop the frozen tunnel.
3. Run the `ssh` command again to generate a fresh link.
