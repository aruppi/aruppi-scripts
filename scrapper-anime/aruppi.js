const fs = require('fs');
const path = require('path');
const urlparser = require('url');
const { Builder, By, Key, until, promise } = require('selenium-webdriver');
const { ServiceBuilder, Options } = require('selenium-webdriver/chrome');
const fuzz = require('fuzzball');

let service = new ServiceBuilder(path.join(__dirname + '/chromedriver.exe'));

const screen = {
    width: 1900,
    height: 980
};

// Here you put the name of the anime
generalScrapper('World Trigger');

async function generalScrapper(animeTitle) {
    
    // Starting the driver
    let driver = await new Builder()
    .forBrowser('chrome')
    .setChromeOptions(new Options().windowSize(screen))
    .setChromeService(service)
    .build();
    
    let animeObj = {};
    let animeFlvObj;
    let malObj;

    try {
        animeFlvObj = await animeFlv(animeTitle, driver);
        malObj = await myAnimeList(animeTitle, driver);
    } catch(error) {
        console.log(error);
    }

    animeObj['id'] = animeFlvObj.id;
    animeObj['title'] = animeFlvObj.title;
    animeObj['genres'] = animeFlvObj.genres;
    animeObj['state'] = animeFlvObj.state;
    animeObj['description'] = animeFlvObj.description;
    animeObj['jkanime'] = false;
    
    if (malObj) {
        animeObj['score'] = malObj.score;
        animeObj['poster'] = malObj.poster;
        animeObj['mal_id'] = malObj['mal_id'];
    }else {
        animeObj['mal_info'] = "No info anime";
        return animeObj;
    }

    // Just for testing
    console.log(animeObj);

    
}

// Function to scrappe animeflv
async function animeFlv(animeTitle, driver) {
    
    let animeObj = {};

    try {
        await driver.get('https://www3.animeflv.net/');
    } catch(error) {
        console.log(error);
        return;
    }

    let buttonCookies = await driver.wait(until.elementLocated(By.id('CybotCookiebotDialogBodyButtonAccept'), 20000));
    
    await buttonCookies.click();

    let searchBar = await driver.findElement(By.id('search-anime'));

    await searchBar.sendKeys(animeTitle); 

    await searchBar.sendKeys(Key.ENTER);

    let listOfAnimes = await driver.findElements(By.css('h3.Title'));

    for (let anime of listOfAnimes) {
        if (fuzz.ratio(await anime.getText(), animeTitle) > 90) {
            await anime.click();
            break;
        }
    }

    animeObj['id'] = urlparser.parse(await driver.getCurrentUrl()).pathname.split('/')[2];
    animeObj['title'] = await driver.findElement(By.css('h1.Title')).getText();
    let genres = await driver.findElements(By.css('.Nvgnrs a'));
    animeObj['genres'] = await promise.map(genres, genre => genre.getText());
    animeObj['state'] = await driver.findElement(By.css('.AnmStts')).getText();
    animeObj['description'] = await driver.findElement(By.css('.Description')).getText();
    animeObj['jkanime'] = false;

    return animeObj;
}


// Function to scrappe myAnimeList
async function myAnimeList(animeTitle, driver) {
    let animeInfo = {};
    let cookiesMal = false;

    try {
        await driver.get('https://myanimelist.net/anime.php');
    } catch(error) {
        console.log(error);
        return;
    }

    try {
        cookiesMal = await driver.wait(until.elementLocated(By.xpath('//div[@id="qc-cmp2-ui"]'), 6000));
    } catch(error) {
        console.log(error);
    }

    if (cookiesMal) {
        await cookiesMal.findElement(By.xpath('//button[text()="AGREE"]')).click();
        
        let searchBar = await driver.findElement(By.css('input.js-advancedSearchText'));

        await searchBar.sendKeys(animeTitle);

        let listAnimes = await driver.wait(until.elementsLocated(By.css("div.info.anime div.name"), 6000));

        
        for (let anime of listAnimes) {
            if (fuzz.ratio(await anime.getText(), animeTitle) > 90) {
                await anime.click();

                let parsedUrl = urlparser.parse(await driver.getCurrentUrl());
                parsedUrl.path = parsedUrl.path.split("/");
        
                try {
                    animeInfo['score'] = await driver.wait(until.elementLocated(By.css('div.score-label'), 3000)).getText();
                    animeInfo['poster'] = await driver.findElement(By.css('img.lazyloaded')).getAttribute('src');
                    animeInfo['mal_id'] = parsedUrl.path[2];
                } catch(error) {
                    driver.quit();
                    return false;
                }

                driver.quit();
                return animeInfo;
            }
        }
       
        driver.quit();
        return false;
       
    }else {
        let searchBar = await driver.findElement(By.css('input.js-advancedSearchText'));

        await searchBar.sendKeys(anime_title);

        let listAnimes = await driver.wait(until.elementsLocated(By.css("div.info.anime div.name"), 6000));

       
        for (let anime of listAnimes) {
            if (fuzz.ratio(await anime.getText(), anime_title) > 90) {
                await anime.click();
                
                let parsedUrl = urlparser.parse(await driver.getCurrentUrl());
                parsedUrl.path = parsedUrl.path.split("/");

                try {
                    animeInfo['score'] = await driver.wait(until.elementLocated(By.css('div.score-label'), 3000)).getText();
                    animeInfo['poster'] = await driver.findElement(By.css('img.lazyloaded')).getAttribute('src');
                    animeInfo['mal_id'] = parsedUrl.path[2];
                } catch(error) {
                    driver.quit();
                    return false;
                }
                

                driver.quit();
                return animeInfo;
            }
        }
        
        driver.quit();
        return false;
    }
}