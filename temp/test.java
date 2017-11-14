public class HelloWorld {

    public static void main(String[] args) {
        
        Set<TaskResult> results = new HashSet<>();
        for (Task t : tasks) {
            t.execute();
            results.add(t.getResult());
        }

    }

}


