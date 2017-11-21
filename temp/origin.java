public class HelloWorld {
    
        public static void main(String[] args) {

            try {
                for (Task t : tasks) {
                    t.execute();
                }
            } catch (Exception e) {
                int a = 10;
            }
        }
    }