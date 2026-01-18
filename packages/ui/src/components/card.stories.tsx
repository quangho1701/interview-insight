import type { Meta, StoryObj } from "@storybook/react";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "./card";
import { Button } from "./button";

const meta: Meta<typeof Card> = {
    title: "UI/Card",
    component: Card,
    tags: ["autodocs"],
    parameters: {
        backgrounds: { default: "dark" },
    },
};

export default meta;
type Story = StoryObj<typeof Card>;

export const Default: Story = {
    render: (args) => (
        <Card className="w-[350px]" {...args}>
            <CardHeader>
                <CardTitle>Interviewer Profile</CardTitle>
                <CardDescription>Analyze the vibe of your interviewer.</CardDescription>
            </CardHeader>
            <CardContent>
                <p className="text-white/80">
                    This card uses the glassmorphism effect by default to fit the "Professional Futurism" aesthetic.
                </p>
            </CardContent>
            <CardFooter className="flex justify-between">
                <Button variant="outline">Cancel</Button>
                <Button>Analyze</Button>
            </CardFooter>
        </Card>
    ),
};
