# Deploying Smart Seating Arrangement to Vercel

This guide will help you deploy your Smart Seating Arrangement application to Vercel.

## Application Overview

The Smart Seating Arrangement application is a lightweight, rule-based system that:
- Predicts student attendance based on historical patterns and simple rules
- Arranges students optimally across exam rooms
- Prevents students from the same department from sitting next to each other
- Provides visual and exportable seating plans

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for local development)
3. Git repository with your project

## Deployment Steps

### Option 1: Deploy using Vercel Dashboard

1. Push your code to a Git repository (GitHub, GitLab, or Bitbucket)
2. Log in to your Vercel account
3. Click "New Project" on the Vercel dashboard
4. Import your Git repository
5. Configure your project:
   - Framework Preset: Other
   - Build Command: Leave empty (config is in vercel.json)
   - Output Directory: Leave empty
6. Set up environment variables (see Environment Variables section below)
7. Click "Deploy"

### Option 2: Deploy using Vercel CLI

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```
   vercel login
   ```

3. Create a `.vercel.env` file with your environment variables if needed

4. Navigate to your project directory and deploy:
   ```
   cd path/to/smart_seating_arrangement
   vercel
   ```

5. Follow the prompts to complete the deployment

## Configuration Files

The following configuration files are included in the project:

- `vercel.json`: Main configuration for Vercel deployment
- `.vercelignore`: Specifies files to exclude from deployment
- `runtime.txt`: Specifies the Python version
- `requirements.txt`: Lists all Python dependencies (minimal - no ML libraries required)
- `.env.example`: Template for local environment variables

## Environment Variables

The application requires several environment variables to be configured. When deploying to Vercel, you need to add these in the Vercel dashboard:

1. Go to your project in the Vercel dashboard
2. Click on "Settings" > "Environment Variables"
3. Add the following variables:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| SECRET_KEY | Secure key for session management | a-long-random-string |
| DEBUG | Enable debug mode (set to False in production) | False |
| FLASK_ENV | Flask environment | production |
| MAX_UPLOAD_SIZE_MB | Maximum size for file uploads in MB | 16 |
| SESSION_LIFETIME_HOURS | Session timeout duration in hours | 1 |

![Vercel Environment Variables](https://i.imgur.com/example-image.png)

### Environment Variable Security

- Environment variables containing sensitive information (like SECRET_KEY) are encrypted at rest and during deployment
- Vercel provides the option to mark variables as sensitive, which prevents them from being exposed in logs
- For maximum security, generate a strong random string for your SECRET_KEY

### Setting Environment Variables via CLI

If you prefer using the Vercel CLI, you can set environment variables using:

```bash
vercel env add SECRET_KEY
```

This will prompt you to enter the value securely.

## Performance Benefits

This application uses a lightweight rule-based approach instead of machine learning models, which offers several benefits in a serverless environment:
- Faster cold starts
- Reduced memory usage
- No heavy ML dependencies
- Lower computational requirements

## Limitations

When deployed to Vercel's serverless environment:

1. File storage is temporary - uploaded files will be stored in `/tmp` and won't persist between requests
2. Session data might not persist between functions
3. The application is serverless, so long-running operations may time out

## Troubleshooting

If you encounter issues during deployment:

1. Check the Vercel deployment logs
2. Ensure all dependencies are listed in requirements.txt
3. Verify your vercel.json configuration
4. Check for any file path issues (use relative paths)
5. Validate that all required environment variables are set

### Common Issues

1. **Missing environment variables**: If your application is throwing errors after deployment, verify that all environment variables are correctly set in Vercel.

2. **Session issues**: If users are being logged out unexpectedly, check that your SECRET_KEY is properly set and not changing between deployments.

3. **Upload failures**: If file uploads are failing, ensure that the code correctly handles the `/tmp` directory in the serverless environment.

For more help, visit the [Vercel documentation](https://vercel.com/docs) or [Vercel Support](https://vercel.com/support). 