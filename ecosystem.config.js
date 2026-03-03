module.exports = {
  apps: [
    {
      name: 'master-pipeline',
      script: 'Skills/gmail-watcher/scripts/master_pipeline.py',
      interpreter: 'python',
      cwd: 'E:/HC/AI_Employee_Vault',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
      min_uptime: '10s',
      out_file: 'Logs/pm2_master_pipeline.log',
      error_file: 'Logs/pm2_master_pipeline_error.log',
      env_file: '.env'
    },
    {
      name: 'whatsapp-watcher',
      script: 'Skills/whatsapp-watcher/scripts/whatsapp_watcher.py',
      interpreter: 'python',
      cwd: 'E:/HC/AI_Employee_Vault',
      autorestart: true,
      watch: false,
      max_restarts: 5,
      restart_delay: 15000,
      min_uptime: '30s',
      out_file: 'Logs/pm2_whatsapp_watcher.log',
      error_file: 'Logs/pm2_whatsapp_error.log',
      env_file: '.env'
    },
    {
      name: 'linkedin-poster',
      script: 'Skills/linkedin-poster/scripts/linkedin_poster.py',
      interpreter: 'python',
      cwd: 'E:/HC/AI_Employee_Vault',
      autorestart: true,
      watch: false,
      max_restarts: 5,
      restart_delay: 15000,
      min_uptime: '30s',
      out_file: 'Logs/pm2_linkedin_poster.log',
      error_file: 'Logs/pm2_linkedin_poster_error.log',
      env_file: '.env'
    },
    {
      name: 'orchestrator',
      script: 'orchestrator.py',
      interpreter: 'python',
      cwd: 'E:/HC/AI_Employee_Vault',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
      min_uptime: '10s',
      out_file: 'Logs/pm2_orchestrator.log',
      error_file: 'Logs/pm2_orchestrator_error.log',
      env_file: '.env'
    },
    {
      name: 'plan-creator',
      script: 'Skills/plan-creator/scripts/plan_creator.py',
      interpreter: 'python',
      cwd: 'E:/HC/AI_Employee_Vault',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 5000,
      min_uptime: '10s',
      out_file: 'Logs/pm2_plan_creator.log',
      error_file: 'Logs/pm2_plan_creator_error.log',
      env_file: '.env'
    }
  ]
}
