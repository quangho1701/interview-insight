import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "./input";

const meta: Meta<typeof Input> = {
    title: "UI/Input",
    component: Input,
    tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof Input>;

export const Default: Story = {
    args: {
        type: "text",
        placeholder: "Search for an interviewer...",
    },
};

export const WithValue: Story = {
    args: {
        type: "email",
        defaultValue: "hello@vibecheck.ai",
    },
};
