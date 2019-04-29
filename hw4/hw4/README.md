QTM385 HW4 Exam Schedule on the Cloud
=====

## Huilan You 

## Task 1: Lambda Function

To solve task 1, I first reviewed my hw1 and used the code from hw1. 
Then I changed the output of the print_exame_schedule from print statement to a list.
As I used AWS Lambda function called hw4, I copied the code from hw1 and created a function called lambda_handler in lambda-function.py under hw4. 
Last, I configured a test to test the lambda function.
I changed the memory to 640 MB and timeout to 15 minutes max.
As a result, I successfully got the final date for corresponding course ID.

## Task 2: API Gateway

I created a API gateway called exam-API, create a GET method and change the JSON mapping template.
I deployed this API gateway and tested it.

The end point link:

```
https://fl7ll8o9kc.execute-api.us-east-1.amazonaws.com/prod/hw4
```


