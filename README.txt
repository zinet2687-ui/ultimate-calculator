ULTIMATE CALCULATOR — Android project

Files:
- main.py: Kivy calculator app
- buildozer.spec: Android build configuration
- .github/workflows/android.yml: GitHub Actions workflow to build APK

Phone workflow:
1. Extract this ZIP on your phone.
2. Upload the CONTENTS of the folder to the root of your GitHub repository.
   Make sure the .github/workflows/android.yml file is included.
3. Open the repository's Actions tab and select "Build Android APK".
4. If it has not run automatically, press "Run workflow".
5. When the run succeeds, open the run, scroll to Artifacts, and download
   ultimate-calculator-apk. Extract the artifact ZIP to get the APK.

This ZIP is source code, not an already-built APK. GitHub Actions must complete
successfully before an APK is available.
