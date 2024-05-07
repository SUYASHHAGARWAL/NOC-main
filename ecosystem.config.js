{       
   apps: [{
      name: "noc",          
      interpreter: "python3",
      interpreter_args: "manage.py",
      args: ["runserver", "4252"],
      watch: true, // Optional, to enable automatic reloading on file changes
      watch_delay: 1000, // Optional, adjust as needed
   }]
}

