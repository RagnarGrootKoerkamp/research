#define SIDE 80
#define UNEXPLORED_COLOR "#FFFFFF"
#define EXPLORED_COLOR "#8888FF"
#define CURRENT_COLOR "#00FF00"
#define DEPENDENCY_COLOR "#000088"
#define HIGHLIGHTING_COLOR "#E64E4E"
#define LAST_COLOR "#FF0000"
#define COLOR_STR_LEN 8
#define DEBUG

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <sys/stat.h>
#include <io.h>

#ifdef __linux
char slash = '/';
#else
char slash = '\\';
#endif // __linux

char doc_start[1000];
char doc_end[1000];
char path[10000];
int d0;
int dist;
char* drawed;
int draw_len;
const int START_Y = SIDE/2;
int START_X;
int FRAME_SIZE;
double duration;
char* A;

int k_to_diag(int i, int k){
    return k - i;
}

bool is_in_range(int cost, int k){
    if(cost < 0 || cost >= dist || k > cost || k < -cost) return false;
    return true;
}

struct node{
    int cost;
    int d;
};

bool put_color(int frame, struct node a, const char* color){
    if(!is_in_range(a.cost,a.d)) return false;
    strcpy(A + (frame*FRAME_SIZE + a.cost*a.cost + a.cost + a.d) * COLOR_STR_LEN,color);
    return true;
}

const char* get_color(int frame, struct node a){
    return A + (frame*FRAME_SIZE + a.cost*a.cost + a.cost + a.d) * COLOR_STR_LEN;
}

struct stack{
    struct node* data;
    int size;
    int max_len;
};

struct draw_set{
    struct stack;
    char color[10];
};

struct stack highlighted;
struct stack last_st;

struct stack new_stack(int max_len){
    struct node* p = (struct node*)malloc(max_len*sizeof(struct node));
    struct stack ret_value = {p, 0, max_len};
    return ret_value;
}

void clear_stack(struct stack* s){
    s->size = 0;
}

bool add_stack(struct stack* main,struct stack* add){
    if(main->size + add->size > main->max_len){
        return false;
    }
    int i;
    //make memcpy instead of a for loop
    for(i = 0; i < add->size; ++i){
        (main->data)[main->size + i] = (add->data)[i];
    }
    main->size += add->size;
    return true;
}

bool stack_push(struct stack* s, struct node el){
    if((s->size) < (s->max_len)){
        (s->data)[s->size] = el;
        (s->size) = (s->size) + 1;
        return true;
    }
    else
        return false;
}

bool copy_stack(struct stack* src, struct stack* dest){
    if(dest->max_len < src->max_len)
        return false;
    int i;
    //make memcpy instead of a for loop
    for(i = 0; i < src->size; ++i){
        dest->data[i] = src->data[i];
    }
    dest->size = src->size;
    return true;
}

void swap_stacks(struct stack* s1, struct stack* s2){
    struct stack* tmp = s1;
    s1 = s2;
    s2 = tmp;
}

struct point{
    int x;
    int y;
};

void generate_rect_with_anim(struct point pos, int stroke_width, int width, int height, char* color, int steps, int cur_frame, FILE* fd){
    char values[10000] = "";
    char key_times[10000] = "";
    if (cur_frame == 0){
        strcat(values,"inline;none;none");
        sprintf(key_times,"0;%.5lf;1",1./steps);
    }
    else if(cur_frame == steps - 1){
        strcat(values,"none;inline;none");
        sprintf(key_times,"0;%.5lf;1",((double)(steps-1))/steps);
    }
    else{
        strcat(values,"none;inline;none;none");
        sprintf(key_times,"0;%.5lf;%.5lf;1",((double)(cur_frame))/steps,((double)(cur_frame+1))/steps);
    }
    char str[10000];
    sprintf(str,"<rect x=\"%d\" y=\"%d\" width=\"%d\" height=\"%d\" fill=\"%s\" stroke=\"#000000\" stroke-width=\"%d\" pointer-events=\"all\">\n<animate id=\"frame1\" attributeName=\"display\" values=\"%s\" keyTimes=\"%s\" dur=\"%lfs\" begin=\"0s\" repeatCount=\"indefinite\" />\n</rect>\n",pos.x,pos.y,width,height,color,stroke_width,values,key_times,duration);
    fputs(str,fd);
}

void generate_rect(char* str, struct point pos, int stroke_width, int width, int height, char* color, int steps, int cur_frame, FILE* fd){
    str[0] = 0;
    sprintf(str,"<rect x=\"%d\" y=\"%d\" width=\"%d\" height=\"%d\" fill=\"%s\" stroke=\"#000000\" stroke-width=\"%d\" pointer-events=\"all\"/>\n",pos.x,pos.y,width,height,color,stroke_width);
    generate_rect_with_anim(pos,stroke_width,width,height,color,steps,cur_frame,fd);
}

char was_drawn(struct node a){
    if(a.cost < 0 || a.cost > dist || a.d > a.cost || a.d < -a.cost){
        exit(2);
    }
    return drawed[a.cost * a.cost + a.cost + a.d];
}

void set_drawn(struct node a, char drawn){
    drawed[a.cost * a.cost + a.cost + a.d] = drawn;
}

struct point get_coord(struct node a){
    if(a.cost < 0 || a.cost > dist || a.d > a.cost || a.d < -a.cost){
        exit(1);
    }
    struct point ret_val = {START_X - SIDE/2 + SIDE * (a.d), START_Y + a.cost * SIDE};
    return ret_val;
};

struct stack highlight_diag(int d){
    struct node a = {0,d};
    bool f = false;
    int cost = 0;
    while(!f && cost < dist){
        f = is_in_range(cost,d);
        if(f) break;
        ++cost;
        a.cost+=1;
    }
    struct stack st = new_stack(dist);
    while(1){
        if(is_in_range(cost,d)){
            if(!stack_push(&st,a)) exit(-21);
        }
        else return st;
        ++cost;
        a.cost+=1;
    }
    exit(-20);
}

void draw_squares(struct stack* nodes, char* color, FILE* fd, FILE* fd_anim, int steps, int cur_frame){
    int i;
    char str[10000];
    if(nodes){
        for(i = 0; i < nodes->size; ++i){
            if (was_drawn((nodes->data)[i])){
                continue;
            }
            if(!put_color(cur_frame,(nodes->data)[i],color)) exit(-21);
            generate_rect(str,get_coord((nodes->data)[i]),4,SIDE,SIDE,color,steps,cur_frame,fd_anim);
            fputs(str,fd);
            set_drawn((nodes->data)[i],1);
        }
    }
    else{
        int k;
        struct node a = {0,0};
        for(i = 0; i < dist; ++i){
            a.cost = i;
            a.d = -i;
            for(k = 0; k <= 2*i; ++k){
                if(was_drawn(a)){
                    set_drawn(a,0);
                }
                else{
                    if(!put_color(cur_frame,a,color)) exit(-22);
                    generate_rect(str,get_coord(a),4,SIDE,SIDE,color,steps,cur_frame,fd_anim);
                    fputs(str,fd);
                }
                ++a.d;
            }
        }
    }
}

void print_node(char* str, struct node n){
    char tmp[1000];
    strcpy(tmp,str);
    sprintf(str,"%scost: %d\tdiagonal: %d\n",tmp,n.cost,n.d);
}

void print_stack(char* str, struct stack* st){
    for(int i = 0; i < st->size; ++i){
        print_node(str,(st->data)[i]);
    }
}

void print(char* msg, struct stack* s){
    char tmp[1000];
    tmp[0] = 0;
    printf("%s\nExplored; size: %d\tmax_len: %d\n",msg,s->size,s->max_len);
    print_stack(tmp,s);
    puts(tmp);
}

bool existDir(const char * name)
{
    struct stat s;
    if (stat(name,&s)) return false;
    return S_ISDIR(s.st_mode);
};

void draw_image(struct stack* current, struct stack* dependency, struct stack* explored, struct stack* highlighted, struct stack* last, const char* name, int file_number,FILE* anim, int steps, int cur_frame){ //if node.cost == -1 => end of the list
    char file_dir[1000] = "";
    sprintf(file_dir,"%s%s",path,name);
    if(!existDir(file_dir)){
        mkdir(file_dir);
    }
    char file_path[10000] = "";
    sprintf(file_path,"%s%s%c%d.svg",path,name,slash,file_number);
    FILE* fd = fopen(file_path,"w");

    fputs(doc_start,fd);

    if(current) draw_squares(current,CURRENT_COLOR,fd,anim,steps,cur_frame);
    if(dependency) draw_squares(dependency,DEPENDENCY_COLOR,fd,anim,steps,cur_frame);
    if(last) draw_squares(last,LAST_COLOR,fd,anim,steps,cur_frame);
    if(explored) draw_squares(explored,EXPLORED_COLOR,fd,anim,steps,cur_frame);
    if(highlighted) draw_squares(highlighted,HIGHLIGHTING_COLOR,fd,anim,steps,cur_frame);
    draw_squares(NULL,UNEXPLORED_COLOR,fd,anim,steps,cur_frame);

    fputs(doc_end,fd);
}

FILE* create_animation(const char* path, const char* name,int steps){
    A = (char*)malloc(steps*dist*dist*COLOR_STR_LEN);

    if(!A){
        printf("Memory allocation error!\nFunction: %s\nLine: %d\nFile: %s",__FUNCTION__,__LINE__,__FILE__);
        exit(-25);
    }

    char file_dir[1000] = "";
    sprintf(file_dir,"%s%s",path,name);
    if(!existDir(file_dir)){
        mkdir(file_dir);
    }
    char file_path[1000];
    sprintf(file_path,"%s%s%cold_%s.svg",path,name,slash,name);

    FILE* fd = fopen(file_path,"w");
    fputs(doc_start,fd);
    return fd;
}

void opt_generate_rect_with_anim(int stroke_width, int width, int height, struct node a, int steps, FILE* fd){
    struct point pos = get_coord(a);
    char values[10000] = "";
    char key_times[10000] = "";
    char color[100] = "";
    char key[100] = "";

    //FRAME 0
    sprintf(color,"%s;",get_color(0,a));
    strcat(values,color);
    sprintf(key_times,"0;");

    for(int frame = 1; frame < steps; ++frame){
        if(strcmp(get_color(frame-1,a),get_color(frame,a))){
            /*sprintf(color,"%s;",get_color(frame-1,a));
            strcat(values,color);
            sprintf(key,"%.5lf;",(double)frame/steps - 0.00001);
            strcat(key_times,key);*/

            sprintf(color,"%s;",get_color(frame,a));
            strcat(values,color);
            sprintf(key,"%.5lf;",(double)frame/steps);
            strcat(key_times,key);
        }
    }

    //LAST FRAME
    sprintf(color,"%s",get_color(steps-1,a));
    strcat(values,color);
    strcat(key_times,"1");

    char str[10000];
    sprintf(str,"<rect x=\"%d\" y=\"%d\" width=\"%d\" height=\"%d\" fill=\"%s\" stroke=\"#000000\" stroke-width=\"%d\" pointer-events=\"all\">\n"
            "<animate id=\"frame1\" calcMode = \"discrete\" attributeName=\"fill\" values=\"%s\" keyTimes=\"%s\" dur=\"%lfs\" begin=\"0s\" repeatCount=\"indefinite\" />\n"
            "</rect>\n",pos.x,pos.y,width,height,color,stroke_width,values,key_times,duration);
    fputs(str,fd);
}

void end_animation(FILE* anim_file, const char* name, int steps){
    fputs(doc_end,anim_file);
    fclose(anim_file);

    //TODO: create optimized svg animation file here
    char file_path[1000];
    sprintf(file_path,"%s%s%c%s.svg",path,name,slash,name);

    FILE* fd = fopen(file_path,"w");
    fputs(doc_start,fd);

    struct node nd;
    for(int row = 0; row < dist; ++row){
        for(int diagonal = -row; diagonal <= row; ++diagonal){
            nd.cost = row;
            nd.d = diagonal;
            opt_generate_rect_with_anim(4,SIDE,SIDE,nd,steps,fd);
        }
    }

    fputs(doc_end,fd);
    fclose(fd);

    if(!A) exit(-23);
    free(A);
    A = NULL;
}

int diamond_steps(){
    int N = dist - abs(d0);
    if(N%2 == 0){
        return (2*abs(d0) + N) * (N / 2) + 1;
    }
    else{
        N+=1;
        return (2*abs(d0) + N) * (N / 2) - N;
    }
}

void diamond(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(2*dist);
    struct stack expl = new_stack(dist*dist);
    int k0 = -1;
    int k1 = d0 + 1;
    int start_cost = 0;
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int k = 0; k < dist - abs(d0); ++k){
        if(k%2 == 1){
            start_cost+=1;
        }
        else{
            k0 += 1;
            k1 -= 1;
        }

        for(int i = k0; i > d0; --i){
            int cur_cost = start_cost + (k0 - i);
            clear_stack(&dep);
            clear_stack(&cur);
            struct node cur_node = {cur_cost, i};
            if(!stack_push(&cur,cur_node)) exit(-3);

            if(is_in_range(cur_cost - 1,i)){
                struct node tmp = {cur_cost - 1,i};
                if(!stack_push(&dep,tmp)) exit(-4);
            }

            if(is_in_range(cur_cost - 1,i + 1)){
                struct node tmp = {cur_cost - 1,i + 1};
                if(!stack_push(&dep,tmp)) exit(-5);
            }

            if(is_in_range(cur_cost - 1,i - 1)){
                struct node tmp = {cur_cost - 1,i - 1};
                if(!stack_push(&dep,tmp)) exit(-6);
            }

            draw_image(&cur,&dep,&expl,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
            ++num;

            stack_push(&expl,cur_node);
        }
        for(int i = k1; i <= d0; ++i){
            int cur_cost = start_cost + abs(d0) + (i - k1);
            clear_stack(&dep);
            clear_stack(&cur);
            struct node cur_node = {cur_cost, i};
            if(!stack_push(&cur,cur_node)) exit(-3);

            if(is_in_range(cur_cost - 1,i)){
                struct node tmp = {cur_cost - 1,i};
                if(!stack_push(&dep,tmp)) exit(-4);
            }

            if(is_in_range(cur_cost - 1,i + 1)){
                struct node tmp = {cur_cost - 1,i + 1};
                if(!stack_push(&dep,tmp)) exit(-5);
            }

            if(is_in_range(cur_cost - 1,i - 1)){
                struct node tmp = {cur_cost - 1,i - 1};
                if(!stack_push(&dep,tmp)) exit(-6);
            }

            draw_image(&cur,&dep,&expl,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
            ++num;

            stack_push(&expl,cur_node);
        }
    }
    draw_image(NULL,NULL,&expl,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

int diamond_parallel_steps(){
    return dist - abs(d0) + 1;
}

void diamond_parallel(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(10*dist);
    struct stack expl = new_stack(dist*dist);
    int k0 = -1;
    int k1 = d0 + 1;
    int start_cost = 0;
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int k = 0; k < dist - abs(d0); ++k){
        if(k%2 == 1){
            start_cost+=1;
        }
        else{
            k0 += 1;
            k1 -= 1;
        }

        clear_stack(&cur);
        clear_stack(&dep);

        for(int i = k0; i > d0; --i){
            int cur_cost = start_cost + (k0 - i);
            struct node cur_node = {cur_cost, i};
            if(!stack_push(&cur,cur_node)) exit(-3);

            if(is_in_range(cur_cost - 1,i)){
                struct node tmp = {cur_cost - 1,i};
                if(!stack_push(&dep,tmp)) exit(-4);
            }

            if(is_in_range(cur_cost - 1,i + 1)){
                struct node tmp = {cur_cost - 1,i + 1};
                if(!stack_push(&dep,tmp)) exit(-5);
            }

            if(is_in_range(cur_cost - 1,i - 1)){
                struct node tmp = {cur_cost - 1,i - 1};
                if(!stack_push(&dep,tmp)) exit(-6);
            }

            if(!stack_push(&expl,cur_node)) exit(-10);
        }

        for(int i = k1; i <= d0; ++i){
            int cur_cost = start_cost + abs(d0) + (i - k1);
            struct node cur_node = {cur_cost, i};
            if(!stack_push(&cur,cur_node)) exit(-3);

            if(is_in_range(cur_cost - 1,i)){
                struct node tmp = {cur_cost - 1,i};
                if(!stack_push(&dep,tmp)) exit(-4);
            }
            if(is_in_range(cur_cost - 1,i + 1)){
                struct node tmp = {cur_cost - 1,i + 1};
                if(!stack_push(&dep,tmp)) exit(-5);
            }
            if(is_in_range(cur_cost - 1,i - 1)){
                struct node tmp = {cur_cost - 1,i - 1};
                if(!stack_push(&dep,tmp)) exit(-6);
            }

            if(!stack_push(&expl,cur_node)) exit(-11);
        }

        draw_image(&cur,&dep,&expl,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
        ++num;
    }
    draw_image(NULL,NULL,&expl,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

void diamond_parallel_mem_save(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(10*dist);
    struct stack expl = new_stack(dist*dist);
    int k0 = -1;
    int k1 = d0 + 1;
    int start_cost = 0;
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int k = 0; k < dist - abs(d0); ++k){
        if(k%2 == 1){
            start_cost+=1;
        }
        else{
            k0 += 1;
            k1 -= 1;
        }

        clear_stack(&cur);
        clear_stack(&dep);

        for(int i = k0; i > d0; --i){
            int cur_cost = start_cost + (k0 - i);
            struct node cur_node = {cur_cost, i};
            if(!stack_push(&cur,cur_node)) exit(-3);

            if(is_in_range(cur_cost - 1,i)){
                struct node tmp = {cur_cost - 1,i};
                if(!stack_push(&dep,tmp)) exit(-4);
            }

            if(is_in_range(cur_cost - 1,i + 1)){
                struct node tmp = {cur_cost - 1,i + 1};
                if(!stack_push(&dep,tmp)) exit(-5);
            }

            if(is_in_range(cur_cost - 1,i - 1)){
                struct node tmp = {cur_cost - 1,i - 1};
                if(!stack_push(&dep,tmp)) exit(-6);
            }

            if(!stack_push(&expl,cur_node)) exit(-10);
        }

        for(int i = k1; i <= d0; ++i){
            int cur_cost = start_cost + abs(d0) + (i - k1);
            struct node cur_node = {cur_cost, i};
            if(!stack_push(&cur,cur_node)) exit(-3);

            if(is_in_range(cur_cost - 1,i)){
                struct node tmp = {cur_cost - 1,i};
                if(!stack_push(&dep,tmp)) exit(-4);
            }
            if(is_in_range(cur_cost - 1,i + 1)){
                struct node tmp = {cur_cost - 1,i + 1};
                if(!stack_push(&dep,tmp)) exit(-5);
            }
            if(is_in_range(cur_cost - 1,i - 1)){
                struct node tmp = {cur_cost - 1,i - 1};
                if(!stack_push(&dep,tmp)) exit(-6);
            }

            if(!stack_push(&expl,cur_node)) exit(-11);
        }

        draw_image(&cur,&dep,NULL,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
        ++num;
    }
    draw_image(NULL,NULL,&cur,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

void add_dependencies(struct stack* s, int i, int k){ // i -cost; k - diagonal
    if(is_in_range(i-1,k-1)){
        struct node tmp = {i-1,k-1};
        if(!stack_push(s,tmp)) exit(-15);
    }
    if(is_in_range(i-1,k)){
        struct node tmp = {i-1,k};
        if(!stack_push(s,tmp)) exit(-16);
    }
    if(is_in_range(i-1,k+1)){
        struct node tmp = {i-1,k+1};
        if(!stack_push(s,tmp)) exit(-17);
    }
}

int WFA_steps(){
    return dist*dist + 1;
}
int WFA_parallel_steps(){
    return dist+1;
}

void WFA(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(2*dist);
    struct stack expl = new_stack(dist*dist);
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int i = 0; i < dist; ++i){
        for(int k = -i; k <= i; ++k){
            struct node cur_node = {i,k};
            stack_push(&cur,cur_node);
            stack_push(&expl,cur_node);

            add_dependencies(&dep,i,k);

            draw_image(&cur,&dep,&expl,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
            ++num;

            clear_stack(&cur);
            clear_stack(&dep);
        }
    }

    draw_image(NULL,NULL,&expl,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

void WFA_mem_save(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(2*dist);
    struct stack expl_prev = new_stack(dist*dist);
    struct stack expl_next = new_stack(dist*dist);
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int i = 0; i < dist; ++i){
        for(int k = -i; k <= i; ++k){
            struct node cur_node = {i,k};
            stack_push(&cur,cur_node);
            stack_push(&expl_prev,cur_node);
            stack_push(&expl_next,cur_node);

            add_dependencies(&dep,i,k);

            draw_image(&cur,&dep,&expl_prev,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
            ++num;

            clear_stack(&cur);
            clear_stack(&dep);
        }
        struct stack tmp = expl_prev;
        expl_prev = expl_next;
        expl_next = tmp;
        clear_stack(&expl_next);
    }

    draw_image(NULL,NULL,&expl_prev,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

void WFA_parallel(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(10*dist);
    struct stack expl = new_stack(dist*dist);
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int i = 0; i < dist; ++i){
        clear_stack(&cur);
        clear_stack(&dep);
        for(int k = -i; k <= i; ++k){
            struct node cur_node = {i,k};
            stack_push(&cur,cur_node);
            stack_push(&expl,cur_node);

            add_dependencies(&dep,i,k);
        }
        draw_image(&cur,&dep,&expl,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
        ++num;
    }

    draw_image(NULL,NULL,&expl,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

void WFA_parallel_mem_save(int steps){
    struct stack cur = new_stack(2*dist);
    struct stack dep = new_stack(10*dist);
    int num = 0;

    FILE* anim_file = create_animation(path,__FUNCTION__,steps);

    for(int i = 0; i < dist; ++i){
        clear_stack(&cur);
        clear_stack(&dep);
        for(int k = -i; k <= i; ++k){
            struct node cur_node = {i,k};
            stack_push(&cur,cur_node);

            add_dependencies(&dep,i,k);
        }
        draw_image(&cur,&dep,NULL,&highlighted,NULL,__FUNCTION__,num,anim_file,steps,num);
        ++num;
    }
    draw_image(NULL,NULL,&cur,&highlighted,&last_st,__FUNCTION__,num,anim_file,steps,num);
    end_animation(anim_file,__FUNCTION__,steps);
}

int main(){
    printf("Enter folder for images (for example C:\\images\\WFA\\; do not forget to change slashes for Linux!): ");
    scanf("%s",path);
    printf("Enter edit distance: ");
    scanf("%d",&dist);
    printf("Enter d0 (len(s1) - len(s2)): ");
    scanf("%d",&d0);
    if(d0 > 0)
        d0 = -d0;

    printf("Enter duration (in seconds): ");
    scanf("%lf",&duration);

    draw_len = (dist + 1) * (dist + 1);
    char buffer[draw_len];
    for(int i = 0; i < draw_len; ++i) buffer[i] = 0;
    drawed = buffer;
    FRAME_SIZE = dist*dist;
    const int IMAGE_WIDTH = SIDE * dist*2;
    const int IMAGE_HEIGHT = SIDE*(dist + 1); //maybe (dist + 2)
    int START_X_tmp = SIDE*dist;
    int n;
    START_X = START_X_tmp;
    doc_start[0] = 0;
    doc_end[0] = 0;
    sprintf(doc_start,"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"%d\" height=\"%d\">\n",IMAGE_WIDTH,IMAGE_HEIGHT);
    sprintf(doc_end,"</svg>");
    highlighted = highlight_diag(d0);
    A = NULL;

    last_st = new_stack(1);
    struct node el = {dist-1,d0};
    stack_push(&last_st,el);

    printf("Diamond...");
    n = diamond_steps();
    diamond(n);
    printf("Done\n\n");

    printf("Diamond parallel...");
    n = diamond_parallel_steps();
    diamond_parallel(n);
    printf("Done\n\n");

    printf("Diamond parallel memory saving...");
    n = diamond_parallel_steps();
    diamond_parallel_mem_save(n);
    printf("Done\n\n");

    printf("WFA...");
    n = WFA_steps();
    WFA(n);
    printf("Done\n\n");

    printf("WFA memory saving...");
    n = WFA_steps();
    WFA_mem_save(n);
    printf("Done\n\n");

    printf("WFA parallel parallel...");
    n = WFA_parallel_steps();
    WFA_parallel(n);
    printf("Done\n\n");

    printf("WFA parallel memory saving...");
    n = WFA_parallel_steps();
    WFA_parallel_mem_save(n);
    printf("Done\n\n");
}
