# MBTI Grouping App

A web application built with **NiceGUI** to automatically group participants based on **MBTI types** and attendance.  
Created in **2025** for the purpose of simplifying group assignment for ESN speedfriending events.

## Features

- Upload **form answer sheet** and **attendance list** in Excel format
- Define which columns correspond to **name, MBTI type, and email**
- Choose grouping modes:
  - Balanced roles
  - Same roles
  - Balanced temperament (SP/NF/NT/SJ)
- Specify number of groups
- Automatically generates participant groups

## Usage

1. Install dependencies:
```bash
pip install pandas nicegui openpyxl
