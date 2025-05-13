#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_WORDS 50
#define MAX_LINE_LEN 1024
#define MAX_ENG_LEN 64
#define MAX_CHS_LEN 896  // 剩下的都给中文解释

typedef struct {
    char english[MAX_ENG_LEN];
    char chinese[MAX_CHS_LEN];
} WordEntry;

int main() {
    FILE *fp = fopen("./3500_1.csv", "r");
    if (fp == NULL) {
        perror("无法打开文件");
        return 1;
    }

    WordEntry wordList[MAX_WORDS];
    int count = 0;
    char line[MAX_LINE_LEN];

    while (fgets(line, sizeof(line), fp) != NULL && count < MAX_WORDS) {
        // 去掉结尾的换行符
        line[strcspn(line, "\r\n")] = '\0';

        char *comma = strchr(line, ',');
        if (comma == NULL) continue;

        // 提取英文单词
        int eng_len = comma - line;
        strncpy(wordList[count].english, line, eng_len);
        wordList[count].english[eng_len] = '\0';

        // 提取中文解释（去掉引号）
        char *chs_start = comma + 1;
        if (*chs_start == '"') chs_start++; // 去掉开头引号
        char *chs_end = strrchr(chs_start, '"');
        if (chs_end) *chs_end = '\0'; // 去掉结尾引号

        strncpy(wordList[count].chinese, chs_start, MAX_CHS_LEN - 1);
        wordList[count].chinese[MAX_CHS_LEN - 1] = '\0';

        count++;
    }

    fclose(fp);

    // 输出读取结果
    printf("已读取 %d 个单词：\n\n", count);
    for (int i = 0; i < count; i++) {
        printf("[%2d] 英文: %s\n", i + 1, wordList[i].english);
        printf("     中文: %s\n\n", wordList[i].chinese);
    }

    return 0;
}




