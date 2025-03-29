# Troubleshooting Vercel Deployment

If you're experiencing issues deploying the Smart Seating Arrangement application to Vercel, here are some common problems and solutions.

## Common Deployment Issues

### 1. Python Version Compatibility

**Problem**: Vercel supports specific Python versions, and your runtime version might not be compatible.

**Solution**:
- Ensure `runtime.txt` specifies a compatible Python version (e.g., `python-3.9`)
- In `vercel.json`, specify the runtime in the config section:
  ```json
  "config": {
    "runtime": "python3.9"
  }
  ```

### 2. Dependency Installation Failures

**Problem**: Some dependencies might fail to install due to version conflicts or compatibility issues.

**Solution**:
- Use flexible version ranges in `requirements.txt` (e.g., `flask>=2.0.1,<3.0.0` instead of `flask==2.0.1`)
- Create a `build.sh` script to customize the installation process
- Add a build command in `vercel.json`:
  ```json
  "buildCommand": "chmod +x build.sh && ./build.sh"
  ```

### 3. Package Conflicts

**Problem**: Certain package combinations might conflict with each other.

**Solution**:
- Use a `pip.conf` file to configure pip behavior
- Install packages one by one in the build script to isolate issues
- Consider using a `constraints.txt` file for more complex dependency management

### 4. Environment Variables

**Problem**: Environment variables not being correctly loaded.

**Solution**:
- Ensure all required environment variables are set in the Vercel dashboard
- Double-check that your code properly loads the `.env` file with python-dotenv
- Verify that environment variable names match exactly between code and dashboard

### 5. File Access Issues

**Problem**: Unable to access files or directories in the deployed environment.

**Solution**:
- Remember that Vercel uses `/tmp` for temporary file storage in serverless functions
- Ensure your code checks if directories exist and creates them if needed
- Use relative paths from the application root when accessing files

## Vercel-Specific Tips

### Function Size Limitation

Vercel has a 50MB size limit for serverless functions. If your deployment is too large:
- Remove unnecessary dependencies
- Use lightweight alternatives for large libraries
- Split your application into multiple serverless functions

### Cold Start Performance

Serverless functions can experience "cold starts." To minimize this:
- Keep your dependency size small
- Optimize import statements to only import what's needed
- Consider using Vercel's Edge Functions for critical paths

### Logs and Debugging

To troubleshoot deployment issues:
1. Check the deployment logs in the Vercel dashboard
2. Use the `vercel logs` command with the Vercel CLI
3. Add additional logging in your application to pinpoint issues

## Testing Locally Before Deployment

You can test your Vercel deployment locally:

1. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Run the dev environment:
   ```
   vercel dev
   ```

This will simulate the Vercel environment locally, helping you catch issues before deploying.

## Getting More Help

If you continue to experience issues:
- Check the [Vercel documentation](https://vercel.com/docs)
- Search the [Vercel GitHub issues](https://github.com/vercel/vercel/issues)
- Post in the [Vercel community](https://github.com/vercel/community)
- Contact Vercel support through the dashboard 