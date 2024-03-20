function showSentiment() {
    var moodDuration = document.getElementById('average_mood').value;
    var moodResult = document.getElementById('mood-result');
    var sentiment = getSentiment(moodDuration); // Assume this function returns the sentiment based on the selected mood duration

    // Clear previous result
    moodResult.innerHTML = '';

    // Display mood result
    var moodMessage;
    if (sentiment === 'happyness') {
        moodMessage = "<span class='happy'>Your student seems happy 😊</span>";
    } else if (sentiment === 'saddness') {
        moodMessage = "<span class='sad'>Your student seems sad 😔</span>";
    } else if (sentiment === 'depression') {
        moodMessage = "<span class='depressed'>Your student seems depressed 😞</span>";
    } else {
        moodMessage = "Unable to determine sentiment.";
    }
    moodResult.innerHTML = moodMessage;
}

function getSentiment(duration) {
    // This function will return the sentiment based on the selected mood duration
    // You can implement this function on the server side using Flask to analyze the student's mood data
    // For demo purposes, we'll just return a random sentiment
    var sentiments = ['happy', 'sad', 'depressed'];
    var randomIndex = Math.floor(Math.random() * sentiments.length);
    return sentiments[randomIndex];
}
