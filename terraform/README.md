# Terraform Root Directory

This directory is the heart of the Terraform setup in this project. It contains all the Terraform modules necessary for deploying server instances into AWS and VMware environments. Here's a breakdown of how it's structured and used:

## Branch-Specific Configuration:

- **Develop and Staging Branches**: For these branches, the VMware module is designated as the Terraform root (TF_ROOT). This means when you're working in either of these branches, Terraform will focus on deploying and managing resources in the VMware infrastructure.
- **Main Branch**: For the main branch, AWS is set as the Terraform root. This configuration directs Terraform to deploy and manage resources in the AWS cloud environment when working from the main branch.
