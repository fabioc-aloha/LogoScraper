# Getting Started

1. **Install dependencies:**
   ```powershell
   ./prepare_env.bat
   ```
2. **Prepare your Excel data:** Columns: `ID`, `CompanyName`, `WebsiteURL` (optional), `Country` (optional)
3. **Run the tool:**
   ```powershell
   python main.py --input "Companies.xlsx" --output "logos"
   ```
4. **Need help?**
   ```powershell
   python main.py --help
   ```

For more usage examples, see the README or run with `--help`.
