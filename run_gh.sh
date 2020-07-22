terminal-notifier -message "Running IG posting 🌱"
echo "💚 RUNNING PESTOFREAKS AUTOMATED POSTING"

echo "🌱 Scraping Pesto Freaks"
instagram-scraper pestofreaks 

echo "🌱 Scraping Tags"
instagram-scraper pesto pastapesto pestosauce pestofresco pestoallagenovese pestoligure pastaalpesto pestoalpesto gnocchialpesto pestogenovese trofiealpesto pestopasta --tag --media-metadata --maximum 5

echo "🌱 Running Python"
python3 image_post.py

rm -rf pesto
rm -rf pastapesto
rm -rf pestosauce
rm -rf gnocchialpesto
rm -rf pestogenovese
rm -rf trofiealpesto
rm -rf pestopasta
rm -rf pestofreaks
rm -rf pestofresco
rm -rf pestoallagenovese
rm -rf pastaalpesto
rm -rf pestoalpesto
rm -rf pestoligure

terminal-notifier -message "Finished running IG posting 🌱"