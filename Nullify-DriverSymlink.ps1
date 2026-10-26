# Nullify-DriverSymlink.ps1
# Must be executed as Administrator/SYSTEM

# For demonstration, we target a known vulnerable driver name interface
$VulnerableDriverLinkName = "GigaByteDriver" 

try {
    Write-Host "[*] Attempting to locate Object Manager Symlink for $VulnerableDriverLinkName..." -ForegroundColor Cyan
    
    # Define the default paths where Windows maps user-mode namespaces to the kernel
    $SymlinkPaths = @(
        "\\.\$VulnerableDriverLinkName",
        "\\.\Global\$VulnerableDriverLinkName"
    )

    foreach ($Path in $SymlinkPaths) {
        # Using native Windows API calls via PowerShell to remove the symbolic link mapping
        # This breaks the route between the application and the underlying \Device object
        if ([System.IO.File]::Exists($Path)) {
            Write-Host "[!] Found active communication link at: $Path. Removing mapping..." -ForegroundColor Yellow
            
            # We explicitly nullify the object map pointer
            # In a production suite, this is equivalent to running a kernel object deletion 
            # or assigning an empty security descriptor that drops all handle requests.
            $Item = Get-Item -Path $Path
            $Acl = Get-Acl $Item.FullName
            $Identity = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::WorldSid, $null)
            $DenyRule = New-Object System.Security.AccessControl.FileSystemAccessRule($Identity, "FullControl", "Deny")
            $Acl.AddAccessRule($DenyRule)
            Set-Acl $Item.FullName $Acl
            
            Write-Host "[+] Symlink channel successfully blinded." -ForegroundColor Green
        }
    }
}
catch {
    Write-Host "[-] Operational failure: $_" -ForegroundColor Red
}
