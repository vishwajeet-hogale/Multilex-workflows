package com.mypkg;

import java.util.HashMap;
import java.util.List;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

public class OpenCorporateSelenium {

	public static void main(String[] args) throws Exception {

				System.setProperty("webdriver.chrome.driver","Resources/chromedriver.exe");

				WebDriver driver = new ChromeDriver();
				driver.get("https://opencorporates.com");
				
				WebDriverWait wait = new WebDriverWait(driver, 20);
				
				wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//input[@name='q']")));
				WebElement weInputTextBox = driver.findElement(By.xpath("//input[@name='q']"));
				
				
				weInputTextBox.sendKeys("DESTREZA SALESFORCE CONSULTING LLC");
			 
				driver.findElement(By.className("oc-home-search_button")).submit();
				Thread.sleep(30000);
				String firstLinkXPath = "//div[@id='results']/ul/li[1]/a[2]";
				
				
				WebElement alink = driver.findElement(By.xpath(firstLinkXPath));
				System.out.println("text = " + alink.getText());
				
				alink.click();
				Thread.sleep(30000);
				String dlXpath = "//div[@id='attributes']/dl";
				WebElement wedl = driver.findElement(By.xpath(dlXpath));
				List<WebElement> wesdt = wedl.findElements(By.xpath("./dt"));
				List<WebElement> wesdd = wedl.findElements(By.xpath("./dd"));
				
				Integer dtCount = wesdt.size();
				HashMap<String, String> hmkv = new HashMap<String, String>();
				
				for(int i=0; i<dtCount; i++) {
					WebElement wedt = wesdt.get(i);
					WebElement wedd = wesdd.get(i);
					
					String header = wedt.getText();
					String value = wedd.getText();
					
					hmkv.put(header, value);
					System.out.println("\n" + header + " ==> " + value );
					

					
				}
				


	}

}


