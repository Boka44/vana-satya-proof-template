# Test automation script for health profile and check-in proofs

Write-Host "`n=== Starting Proof Tests ===`n" -ForegroundColor Cyan

# Function to run proof and display results
function Run-Proof {
    param (
        [string]$TestFile,
        [string]$TestType
    )
    
    Write-Host "Testing $TestType..." -ForegroundColor Yellow
    
    # Create temp directory for testing
    $tempDir = "demo/temp_input"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    # Copy test file to temp directory
    Copy-Item $TestFile "$tempDir/test.json"
    
    # Run container using temp directory
    docker run --rm --volume "${PWD}/demo/sealed:/sealed" --volume "${PWD}/demo/temp_input:/input" --volume "${PWD}/demo/output:/output" --env PYTHONUNBUFFERED=1 --env LOG_LEVEL=DEBUG my-proof
        
    # Read and display results
    $results = Get-Content "demo/output/results.json" | ConvertFrom-Json
    
    Write-Host "`nResults for ${TestType}" -ForegroundColor Green
    Write-Host "Valid: $($results.valid)"
    Write-Host "Score: $($results.score)"
    Write-Host "Quality: $($results.quality)"
    Write-Host "Ownership: $($results.ownership)"
    Write-Host "Authenticity: $($results.authenticity)"
    Write-Host "Uniqueness: $($results.uniqueness)"
    Write-Host ("Attributes: " + ($results.attributes | ConvertTo-Json))
    Write-Host "`n---`n"
    
    # Clean up temp directory
    Remove-Item -Recurse -Force $tempDir
}

# Test Health Profile
Run-Proof -TestFile "demo/input/health_profile.json" -TestType "Health Profile"

# Test Check-in
Run-Proof -TestFile "demo/input/checkin_1.json" -TestType "Daily Check-in"

Write-Host "=== Testing Complete ===`n" -ForegroundColor Cyan 