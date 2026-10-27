# START HERE — Chromebook Linux, tomorrow
## Plain-language first-boot checklist. Do it in order. Stop if a step fails.

### BEFORE YOU START — do not skip these
1. **Unplug every external drive.** Seagate, SSD, the 1.9 TB drive, everything.
   Only the installer SD card stays plugged in. This is how we make sure
   nothing but the Chromebook's own drive gets installed to.
2. **Never format the Seagate, the SSD, or the 1.9 TB drive.** The install
   goes to the Chromebook's internal drive only. That drive is 32 GB.
3. **Do not make a new Cloudflare tunnel token.** Your old token is saved
   in your Seagate backup. We copy it back later. Making a new one would
   break the old tunnel.
4. **Tonight is a test, not an install.** If anything below looks wrong,
   stop and tell Potion. Do not guess.

### STEP 1 — Try it first, do not install yet
1. Plug in the installer SD card and start the Chromebook from it
   (the boot menu you use at the machine — pick the SD card).
2. Wait for the Debian desktop to load. Do not click Install yet.
3. Check these four things:
   - Wi-Fi: can you join your Wi-Fi and open a web page?
   - Sound: does sound play?
   - Touchpad: does the mouse move and click?
   - Suspend: close the lid, wait a few seconds, open it — does it wake up?
4. **If any one of those fails, STOP.** Do not install. Tell Potion
   which one failed. A bad trial means a bad install.

### STEP 2 — Install, only if the trial passed
1. With all external drives STILL unplugged, click Install.
2. When it asks where to install, pick the internal drive only (32 GB).
   Do not pick any USB drive. Do not pick "erase everything" for a USB drive.
3. Make your new Linux username and password. Write the password down
   somewhere safe — you will need it, and Potion does not have it.
4. Let it finish, take the SD card out when it tells you to, and restart
   into your new Linux.

### STEP 3 — First boot: run the easy setup
1. Open a Terminal.
2. Find this setup pack. It is either:
   - on the second partition of the installer SD card, OR
   - in your Seagate backup, if the second partition could not be made.
   (Potion's report will say which one it is — read that first.)
3. Copy the whole setup-pack folder to your home folder, then run:
   ```
   bash scripts/first-boot.sh
   ```
   Type your Linux password when it asks. This installs the normal tools,
   sets the time to New York, and cleans up space for the small 32 GB drive.
4. Then run:
   ```
   bash scripts/tailscale-ssh-setup.sh
   ```
   Then type:
   ```
   sudo tailscale up --ssh
   ```
   It will print a web link. Open that link yourself, sign in with Google,
   and approve the new device. That is the only sign-in step for Tailscale.
   Do not paste that link into chat.

### STEP 4 — Put your tunnel back, from the Seagate only
1. Plug the Seagate back in. Open Files and check you can see your files.
2. Copy this folder back from the Seagate backup:
   `Penguin-Backup-2026-10-26/home/.cloudflared/`
   to your new home folder, as `.cloudflared/` — same name, same files.
   Do not type the token out, do not make a new one, just copy the folder.
3. Run the tunnel starter from the pack:
   ```
   bash home-configs/start-tunnel.sh
   ```
   It reads the token file itself. It does not print the token.

### STEP 5 — Put the AI loop and watchdog back
1. Copy these folders from the setup pack to your home folder:
   `agent-loop/`, `tells-v2/`, `pool/`, `bridge-watch/`
2. Start the watchdog:
   ```
   bash bridge-watch/bridge-watch-v2.sh
   ```
   (If that script says to use a different start command, use the one
   printed at the top of the script.)
3. Check the basics:
   ```
   tailscale status
   free -m
   df -h
   ```
   You should see Tailscale connected, about 4 GB of memory, and the
   32 GB drive with space left.

### STEP 6 — Tell Potion to test it
1. Tell Potion: "Linux is up, test SSH."
2. Potion will try to reach the Chromebook over Tailscale from Muse.
3. If SSH works, you are done. If it does not, do not change anything
   else — tell Potion what the last step said.

### What is in this pack, and what is NOT in it
- IN: first-boot setup, Tailscale/SSH setup, Seagate backup script
  (finds Seagate by its name, never by a drive letter, and only copies —
  it never deletes), AI loop, tells checker, card pool (8,658 cards),
  bridge watchdog, tunnel starter.
- NOT IN: no tunnel token, no service token, no certificate, no SSH key,
  no password. Those come back only from your Seagate backup, or from
  you typing/signing in yourself at first boot.
- Cameras and voice auto-start are NOT in this pack. They stay off
  until you approve them separately, camera by camera.

### If you get stuck
Stop at the step that failed, write down exactly what the screen said,
and tell Potion. Do not re-run the install, do not re-format a drive,
and do not try a different drive letter on your own — drive letters
change every time you restart, and picking the wrong one erases data.
