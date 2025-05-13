#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_WORDS 1000
#define LINE_LEN 256

typedef struct {
    char english[64];
    char chinese[128];
} WordEntry;

WordEntry wordList[MAX_WORDS];
int wordCount = 0;

void loadWords(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        perror("词库打开失败");
        exit(EXIT_FAILURE);
    }

    char line[LINE_LEN];
    while (fgets(line, LINE_LEN, fp)) {
        char *token = strtok(line, ",");
        if (!token) continue;

        token = strtok(NULL, ","); // 英文
        if (!token) continue;
        strncpy(wordList[wordCount].english, token, 63);

        token = strtok(NULL, "\n"); // 中文
        if (!token) continue;
        strncpy(wordList[wordCount].chinese, token, 127);

        wordCount++;
    }

    fclose(fp);
}

int getRandomExcept(int exclude) {
    int r;
    do {
        r = rand() % wordCount;
    } while (r == exclude);
    return r;
}

void generateQuestion() {
    int correctIndex = rand() % wordCount;
    int options[4] = {correctIndex, -1, -1, -1};

    // 填充干扰项
    for (int i = 1; i < 4; i++) {
        int idx;
        do {
            idx = getRandomExcept(correctIndex);
            int repeat = 0;
            for (int j = 0; j < i; j++) {
                if (options[j] == idx) repeat = 1;
            }
            if (!repeat) break;
        } while (1);
        options[i] = idx;
    }

    // 打乱顺序
    for (int i = 3; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = options[i];
        options[i] = options[j];
        options[j] = tmp;
    }

    printf("🔍 单词：%s\n", wordList[correctIndex].english);
    printf("请选择正确的中文释义：\n");

    char labels[4] = {'A', 'B', 'C', 'D'};
    int correctOption = -1;

    for (int i = 0; i < 4; i++) {
        printf("%c. %s\n", labels[i], wordList[options[i]].chinese);
        if (options[i] == correctIndex) {
            correctOption = labels[i];
        }
    }

    printf("你的选择");
    char userInput;
    scanf(" %c", &userInput);

    if (userInput == correctOption) {
        printf("回答正确！\n");
    } else {
        printf("回答错误，正确答案是 %c\n", correctOption);
    }
}

int main() {
    srand(time(NULL));
    loadWords("words.csc");

    if (wordCount < 4) {
        printf("词汇量不足，至少需要4个词！\n");
        return 1;
    }

    generateQuestion();

    return 0;
}
