#!/bin/bash

# Universal launcher shell script - no Python dependencies

case "$1" in
    "website")
        if [ -z "$2" ]; then
            echo "Usage: ./launch.sh website <url> [browser]"
            exit 1
        fi

        URL="$2"
        BROWSER="${3:-chrome}"

        # Add https if not present
        if [[ ! "$URL" =~ ^https?:// ]]; then
            URL="https://$URL"
        fi

        case "$BROWSER" in
            "chrome") BROWSER_NAME="Google Chrome" ;;
            "brave") BROWSER_NAME="Brave Browser" ;;
            "safari") BROWSER_NAME="Safari" ;;
            "firefox") BROWSER_NAME="Firefox" ;;
            *) BROWSER_NAME="$BROWSER" ;;
        esac

        echo "🌐 Opening $URL in $BROWSER_NAME..."
        open -a "$BROWSER_NAME" "$URL"
        echo "✅ Done!"
        ;;

    "app")
        if [ -z "$2" ]; then
            echo "Usage: ./launch.sh app <app_name> [path]"
            exit 1
        fi

        APP_NAME="$2"
        FILE_PATH="$3"

        echo "🚀 Launching $APP_NAME..."
        if [ -n "$FILE_PATH" ]; then
            open -a "$APP_NAME" "$FILE_PATH"
            echo "✅ Opened $APP_NAME with $FILE_PATH"
        else
            open -a "$APP_NAME"
            echo "✅ Launched $APP_NAME"
        fi
        ;;

    "list-browsers")
        echo "Available browsers:"
        echo "  chrome   -> Google Chrome"
        echo "  brave    -> Brave Browser"
        echo "  safari   -> Safari"
        echo "  firefox  -> Firefox"
        ;;

    "list-apps")
        echo "Applications in /Applications:"
        ls /Applications | grep '\.app$' | sed 's/\.app$//' | head -20
        ;;

    *)
        echo "Universal Launcher"
        echo "=================="
        echo "Usage:"
        echo "  ./launch.sh website <url> [browser]"
        echo "  ./launch.sh app <app_name> [file_path]"
        echo "  ./launch.sh list-browsers"
        echo "  ./launch.sh list-apps"
        echo ""
        echo "Examples:"
        echo "  ./launch.sh website github.com chrome"
        echo "  ./launch.sh website google.com brave"
        echo "  ./launch.sh app Calculator"
        echo "  ./launch.sh app Windsurf"
        ;;
esac